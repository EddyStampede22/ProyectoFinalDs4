''' Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior, buscará información de cada revista en SCIMAGO 
y la guardará en un nuevo archivo JSON - versión optimizada con multithreading'''
# importar las librerías necesarias
import json
import requests
from bs4 import BeautifulSoup
import time
import random
import os
import hashlib
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import leer_csv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraping.log"),
        logging.StreamHandler()
    ]
)

# Variables compartidas con protección de concurrencia
lock = threading.Lock()
session_local = threading.local()
resultados = {}
contador = {'procesados': 0, 'total': 0, 'encontrados': 0, 'no_encontrados': 0}

# Crear las funciones necesarias para el web scrapper

def leer_json_seguro(archivo:str):
    """
    Lee un archivo JSON y maneja errores de lectura.
    
    Args:
        archivo (str): Ruta al archivo JSON a leer.
    
    Returns:
        dict: Contenido del archivo JSON como diccionario, o None si hubo un error.
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error al leer el archivo {archivo}: {e}")
        return None

def get_session():
    """Obtiene una sesión HTTP para el hilo actual"""
    if not hasattr(session_local, "session"):
        session_local.session = requests.Session()
        retries = Retry(
            total=3,                   # hasta 3 reintentos
            backoff_factor=1,          # espera progresiva: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        session_local.session.mount("https://", HTTPAdapter(max_retries=retries))
    return session_local.session

def get_soup_with_cache(url, cache_dir="cache"):
    """Obtiene el soup de una URL con caché para evitar peticiones repetidas"""
    # Crear directorio de caché si no existe
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    # Crear un nombre de archivo hash basado en la URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{url_hash}.html")
    
    # Si existe en caché, usar eso
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return BeautifulSoup(content, "html.parser")
    
    # Si no, hacer la petición y guardar en caché
    soup = get_soup(url)
    if soup:
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    return soup

def get_soup(url):
    """Realiza una petición HTTP y devuelve un objeto BeautifulSoup"""
    # Obtener sesión para este hilo
    session = get_session()
    
    # Cabeceras para emular navegador
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.scimagojr.com/"
    }
    
    try:
        # Petición con timeout de 10 segundos
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al solicitar {url}:\n  {e}")
        return None
    
    # Añadir variación aleatoria al tiempo de espera
    time.sleep(random.uniform(0.8, 1.8))
    
    # Crear BeautifulSoup directamente con response
    response = response.content
    response = str(response, 'utf-8')
    return BeautifulSoup(response, "html.parser")

def extraer_enlace_optimizado(url_busqueda, titulo, max_paginas=3):
    """
    Extrae la URL de una revista en SCIMAGO, optimizado para búsqueda en múltiples páginas.
    """
    for pagina in range(1, max_paginas+1):
        # Añadir número de página si no es la primera
        url_con_pagina = f"{url_busqueda}&page={pagina}" if pagina > 1 else url_busqueda
        
        logging.info(f"Buscando '{titulo}' en página {pagina}")
        soup = get_soup_with_cache(url_con_pagina)
        
        if not soup:
            continue
            
        # Buscar el div exterior
        div_exterior = soup.find('div', class_='journaldescription colblock')
        if not div_exterior:
            logging.warning(f"No se encontró div_exterior en página {pagina}")
            continue
            
        # Buscar el div interior
        div_interior = div_exterior.find('div', class_='search_results')
        if not div_interior:
            logging.warning(f"No se encontró div_interior en página {pagina}")
            continue
            
        # Buscar enlace
        enlace = div_interior.find('a')
        if enlace is not None:
            span = enlace.find('span', class_='jrnlname')
            if span:
                    texto = enlace.find('span', class_='jrnlname').text.strip()
                    if texto.lower() == titulo.lower():
                        url_extraida = enlace['href']
                        return url_extraida
        
    return None

def extraer_datos_finales(url_final, nombre_revista, datos_revista):
    """Extrae los datos detallados de una revista"""
    # Crear la entrada para la revista si no existe
    if nombre_revista not in datos_revista:
        datos_revista[nombre_revista] = {}
        
    soup = get_soup_with_cache(url_final)
    if not soup:
        logging.error(f"No se pudo obtener datos para {nombre_revista}")
        return None
        
    main_content = soup.find('div', class_='background')
    if main_content:
        segundo_div = main_content.find('div', class_='journalgrid')
        if segundo_div:
            divs = segundo_div.find_all('div')
            for div in divs:
                if div.find('h2'):
                    h2 = div.find('h2').text.strip()
                    if h2 == "Subject Area and Category":
                        datos_revista[nombre_revista][h2] = {}
                        li = div.find_all('li', style='display: inline-block;')
                        for i in li:
                            if i.find('a'):
                                a = i.find('a').text.strip()
                                datos_revista[nombre_revista][h2][a] = []
                                if i.find('ul', class_='treecategory'):
                                    categoria = i.find('ul', class_='treecategory').find_all('li')
                                    for j in categoria:
                                        if j.find('a'):
                                            b = j.find('a').text.strip()
                                            datos_revista[nombre_revista][h2][a].append(b)
                    elif h2 == "Publisher":
                        datos_revista[nombre_revista][h2] = []
                        p = div.find_all('p')
                        for i in p:
                            if i.find('a'):
                                a = i.find('a').text.strip()
                                datos_revista[nombre_revista][h2].append(a)
                    elif h2 == "SJR 2024":
                        otrah = div.find_all('p')
                        datos_revista[nombre_revista]["H-Index"] = otrah[1].text.strip()
                    elif h2 == "H-Index":
                        p=div.find('p')
                        if p:
                            a = p.text.strip()
                            datos_revista[nombre_revista]["H-Index"] = a 
                    elif h2 == "Publication type":
                        datos_revista[nombre_revista][h2] = []
                        p = div.find_all('p')
                        for i in p:
                            a = i.text.strip()
                            datos_revista[nombre_revista][h2].append(a)
                    elif h2 == "ISSN":
                        p = div.find_all('p')
                        for i in p:
                            a = i.text.strip()
                            datos_revista[nombre_revista][h2] = a
                    elif h2 == "Information":
                        p = div.find_all('p')
                        for i in p:
                            if i.text.strip() == "Homepage":
                                a = i.find('a')['href']
                                datos_revista[nombre_revista]["Homepage"] = a
        else:
            logging.warning(f"No se encontró el segundo div para {nombre_revista}")
            return None
    else:
        logging.warning(f"No se encontró el div principal para {nombre_revista}")
        return None
   
    # Extraer el widget
    datos_revista[nombre_revista]["Widget"] = {}
    content_widget = soup.find_all('div', class_='dashboard')
    if len(content_widget) != 0:
        for content in content_widget:
            content_cell = content.find_all('div', class_='cell1x1 transparentcell')
        for i in content_cell:
            if i.find('img', class_='imgwidget'):
                direccion_img = 'https://www.scimagojr.com/' + i.find('img', class_='imgwidget')['src']
                datos_revista[nombre_revista]['Widget']['Imagen'] = direccion_img
            if i.find('div', class_='widgetlegend'):
                html_content = i.find('div', class_='widgetlegend').find('input')['value']
                if html_content:
                    datos_revista[nombre_revista]['Widget']['HTML Code'] = html_content
    
    return datos_revista

def guardar_resultados_parciales(datos, num):
    """Guarda los resultados obtenidos hasta el momento"""
    if datos:
        # Fusionar con datos existentes si el archivo ya existe
        archivo_parcial = f"revistas_scimago_parcial_{num}.json"
        datos_existentes = leer_json_seguro(archivo_parcial) or {}
        datos_combinados = {**datos_existentes, **datos}
        leer_csv.guardar_como_json(datos_combinados, archivo_parcial)
        logging.info(f"Guardado parcial #{num} completado ({len(datos)} revistas)")

def guardar_estado(ultimo_titulo):
    """Guarda el último título procesado para poder continuar si se interrumpe"""
    with open("ultimo_procesado.txt", "w", encoding='utf-8') as f:
        f.write(ultimo_titulo)

def cargar_estado():
    """Carga el último título procesado"""
    try:
        with open("ultimo_procesado.txt", "r", encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def procesar_revista(titulo, url_base, url_busqueda):
    """Procesa una revista individual en un hilo separado"""
    try:
        # Añadir variación aleatoria al tiempo de espera para evitar patrones detectables
        time.sleep(random.uniform(0.5, 1.0))
        
        # Buscar la revista
        buscar_palabra = titulo.replace(" ", "+").lower()
        nueva_palabra = url_busqueda + buscar_palabra
        
        # Extraer enlace de la página de búsqueda
        logging.info(f"Buscando enlace para: {titulo}")
        palabra_clave = extraer_enlace_optimizado(nueva_palabra, titulo)
        
        if palabra_clave is None:
            with lock:
                contador['procesados'] += 1
                contador['no_encontrados'] += 1
                logging.warning(f"[{contador['procesados']}/{contador['total']}] No se encontró: {titulo}")
            return None
        
        # Si encontramos la revista, extraer datos detallados
        busqueda_maxima = url_base + palabra_clave
        datos = {}  # Crear un diccionario nuevo para cada revista
        logging.info(f"Extrayendo datos de {titulo} en {busqueda_maxima}")
        extraer_datos_finales(busqueda_maxima, titulo, datos)
        
        # Actualizar resultados y contador bajo protección de lock
        with lock:
            contador['procesados'] += 1
            contador['encontrados'] += 1
            # Fusionar los datos en el diccionario global
            resultados.update(datos)
            logging.info(f"[{contador['procesados']}/{contador['total']}] Procesado: {titulo}")
            
            # Guardar estado actual
            guardar_estado(titulo)
            
            # Guardar resultados parciales cada 200 revistas
            if contador['procesados'] % 200 == 0:
                guardar_resultados_parciales(resultados, contador['procesados'])
                
        return datos
    except Exception as e:
        with lock:
            contador['procesados'] += 1
            logging.error(f"[{contador['procesados']}/{contador['total']}] Error procesando {titulo}: {e}")
        return None

if __name__ == "__main__":
    url = "https://www.scimagojr.com/"
    url_busqueda = "https://www.scimagojr.com/journalsearch.php?q=+"
    
    # Cargar datos existentes
    revistas = leer_json_seguro("revistas.json")  
    catalogo = leer_json_seguro("revistas_scimago_parcial_20000.json") or {}
    
    # Verificar que se cargaron correctamente
    if not revistas:
        logging.error("No se pudo cargar el archivo de revistas, terminando ejecución")
        exit(1)
    
    # Cargar el último título procesado si existe
    ultimo_procesado = cargar_estado()
    continuar_desde = False if ultimo_procesado else True
    
    # Filtrar revistas que ya están en el catálogo
    revistas_pendientes = []
    for titulo in revistas:
        # Si hay último procesado y aún no lo hemos encontrado, seguir buscando
        if ultimo_procesado and not continuar_desde:
            if titulo == ultimo_procesado:
                continuar_desde = True
            continue
        
        # Si la revista ya está en el catálogo, saltarla
        if titulo in catalogo:
            logging.info(f"La revista {titulo} ya está en el JSON, saltando")
            continue
            
        revistas_pendientes.append(titulo)
    
    # Inicializar contador
    contador['total'] = len(revistas_pendientes)
    logging.info(f"Total de revistas a procesar: {contador['total']}")
    
    # Si no hay revistas para procesar, terminar
    if contador['total'] == 0:
        logging.info("No hay revistas nuevas para procesar")
        exit(0)
    
    # Número de trabajadores concurrentes (ajustar según necesidades)
    num_trabajadores = 5  # Un buen punto de partida
    
    # Ejecutar con ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_trabajadores) as executor:
        # Crear futuros
        futuros = {executor.submit(procesar_revista, titulo, url, url_busqueda): titulo 
                   for titulo in revistas_pendientes}
        
        # Procesar resultados a medida que se completan
        for futuro in as_completed(futuros):
            titulo = futuros[futuro]
            try:
                # El resultado ya se guardó en el diccionario compartido
                futuro.result()
            except Exception as e:
                logging.error(f"Error no capturado procesando {titulo}: {e}")
    
    # Guardar resultados finales
    if resultados:
        # Combinar con el catálogo existente
        catalogo_actualizado = {**catalogo, **resultados}
        leer_csv.guardar_como_json(catalogo_actualizado, "revistas_scimago_parcial_20000.json")
        logging.info(f"Proceso completado. Revistas encontradas: {contador['encontrados']}")
        logging.info(f"Revistas no encontradas: {contador['no_encontrados']}")
    else:
        logging.info("No se encontraron revistas nuevas")