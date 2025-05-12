''' Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior, buscará información de cada revista en SCIMAGO 
y la guardará en un nuevo archivo JSON'''
# importar las librerías necesarias
import json
import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import leer_csv 
# Crear las funciones necesarias para el web scrapper
    # leer el archivo JSON generado por la parte anterior
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
        print(f"Error al leer el archivo {archivo}: {e}")
        return None

def get_soup(url):
    # 1) Session con reintentos
    session = requests.Session()
    retries = Retry(
        total=3,                   # hasta 3 reintentos
        backoff_factor=1,          # espera progresiva: 1s, 2s, 4s
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    # 2) Cabeceras para emular navegador
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
        # 3) Petición con timeout de 10 segundos
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Error al solicitar {url}:\n  {e}")
        return None
    
    # 4) Opcional: respetar un delay
    time.sleep(1.5)
    
    # 5) Crear BeautifulSoup directamente con response
    response=response.content
    response=str(response, 'utf-8')
    return BeautifulSoup(response, "html.parser")

def extraer_enlace(url_busqueda,titulo:str):
    # Realiza la solicitud HTTP y obtiene el contenido de la página
    soup = get_soup(url_busqueda)
    if soup:
        div_exterior = soup.find('div', class_='journaldescription colblock')

        # Si encontramos el div exterior, buscamos el div interior
        if div_exterior:
            div_interior = div_exterior.find('div', class_='search_results')
            
            # Si encontramos el div interior, buscamos el enlace
            if div_interior:
                enlace = div_interior.find('a')
                if enlace is not None:
                    if enlace.find('span', class_='jrnlname'):
                        texto = enlace.find('span', class_='jrnlname').text.strip()
                        if texto.lower() == titulo.lower():
                            url_extraida = enlace['href']
                            return url_extraida
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                print("No se encontró el div interior")
                return None
        else:
            print("No se encontró el div exterior")
            return None

def extraer_datos_finales(url_final,nombre_revista,datos_revista:dict):
    datos_revista[nombre_revista]={}
    soup = get_soup(url_final)
    if soup:
        main_content=soup.find('div', class_='background')
        if main_content:
            segundo_div = main_content.find('div', class_='journalgrid')
            if segundo_div:
                divs=segundo_div.find_all('div')
                for div in divs:
                    if div.find('h2'):
                        h2=div.find('h2').text.strip()
                        if h2=="Subject Area and Category":
                            datos_revista[nombre_revista][h2]={}
                            li=div.find_all('li',style='display: inline-block;')
                            for i in li:
                                if i.find('a'):
                                    a=i.find('a').text.strip()
                                    datos_revista[nombre_revista][h2][a]=[]
                                    if i.find('ul',class_='treecategory'):
                                        categoria=i.find('ul',class_='treecategory').find_all('li')
                                        for j in categoria:
                                            if j.find('a'):
                                                b=j.find('a').text.strip()
                                                datos_revista[nombre_revista][h2][a].append(b)
                        elif h2=="Publisher":
                            datos_revista[nombre_revista][h2]=[]
                            p=div.find_all('p')
                            for i in p:
                                if i.find('a'):
                                    a=i.find('a').text.strip()
                                    datos_revista[nombre_revista][h2].append(a)
                        elif h2=="SJR 2024":
                            otrah=div.find_all('p')
                            datos_revista[nombre_revista]["H-Index"]= otrah[1].text.strip()

                        elif h2=="Publication type":
                            datos_revista[nombre_revista][h2]=[]
                            p=div.find_all('p')
                            for i in p:
                                    a=i.text.strip()
                                    datos_revista[nombre_revista][h2].append(a)
                        
                        elif h2=="ISSN":
                            p=div.find_all('p')
                            for i in p:
                                    a=i.text.strip()
                                    datos_revista[nombre_revista][h2]=a
                        elif h2=="Information":
                            p=div.find_all('p')
                            for i in p:
                                    if i.text.strip() =="Homepage":
                                        a=i.find('a')['href']
                                        datos_revista[nombre_revista]["Homepage"]=a
            else:
                print("No se encontró el segundo div")
                return None
        else:
            print("No se encontró el div principal")
            return None
       
       # Extraer el widget
        datos_revista[nombre_revista]["Widget"]={}
        content_widget=soup.find_all('div', class_='dashboard')
        if len(content_widget)!=0:
            for content in content_widget:
                content_cell=content.find_all('div', class_='cell1x1 transparentcell')
            for i in content_cell:
                if i.find('img',class_='imgwidget'):
                    direccion_img='https://www.scimagojr.com/'+i.find('img',class_='imgwidget')['src']
                    datos_revista[nombre_revista]['Widget']['Imagen']=direccion_img
                if i.find('div',class_='widgetlegend'):
                    html_content=i.find('div',class_='widgetlegend').find('input')['value']
                    if html_content:
                        datos_revista[nombre_revista]['Widget']['HTML Code']=html_content
        else:
            return None            
    return datos_revista


if __name__ == "__main__":
    url = (
        "https://www.scimagojr.com/"
  )
    url_busqueda = (
        "https://www.scimagojr.com/journalsearch.php?q=+"
    )
    #palabra="YI QI YI BIAO XUE BAO/CHINESE JOURNAL OF SCIENTIFIC INSTRUMENT"
    revistas = leer_json_seguro("revistas.json")  # libros es un dict: {titulo: {...}, ...}
    catalogo = leer_json_seguro("revistas_scimago_20000.json") # libros es un dict: {titulo: {...}, ...}
    mis_revistas = {}
    #buscar_palabra=palabra.replace(" ", "+").lower()
    #print(buscar_palabra)
    #nueva_palabra=url_busqueda+buscar_palabra
    #print(nueva_palabra)
    #palabra_clave=extraer_enlace(nueva_palabra,palabra)
    #print(palabra_clave)
    #busqueda_maxima=url+palabra_clave
    #print(busqueda_maxima)
    #revis=extraer_datos_finales(busqueda_maxima,palabra,mis_revistas)
    #print(revis)
    for titulo in revistas:
        # aquí 'titulo' es ya la clave (el nombre del libro)
        if titulo in catalogo:
            # Si la revista ya está en el JSON, no la vuelvo a añadi
            print(f"La revista {titulo} ya está en el JSON")
        elif titulo not in catalogo:
            buscar_palabra=titulo.replace(" ", "+").lower()
            #print(buscar_palabra)
            nueva_palabra=url_busqueda+buscar_palabra
            #print(nueva_palabra)
            palabra_clave=extraer_enlace(nueva_palabra,titulo)
            #print(palabra_clave)
            if palabra_clave is None:
                print(f"No se encontró la revista {titulo} en SCIMAGO")
                continue
            busqueda_maxima=url+palabra_clave
            #print(busqueda_maxima)
            revista=extraer_datos_finales(busqueda_maxima,titulo,mis_revistas)
    if mis_revistas == {}:
        print("No se encontraron revistas nuevas en SCIMAGO")
    else:
        leer_csv.guardar_como_json(revista, "revistas_scimago.json")