''' Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior, buscará información de cada revista en SCIMAGO 
y la guardará en un nuevo archivo JSON'''
# importar las librerías necesarias
import json
import os
import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# Crear las funciones necesarias para el web scrapper
    # leer el archivo JSON generado por la parte anterior
def leer_json_seguro(archivo):
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


'''revistas = leer_json_seguro("revis.json")  # libros es un dict: {titulo: {...}, ...}
revistas2 = leer_json_seguro("revistas.json") # libros es un dict: {titulo: {...}, ...}

for titulo in revistas:
    # aquí 'titulo' es ya la clave (el nombre del libro)
    info = revistas[titulo]  # p. ej. {'autor': ..., 'año': ...}
    print(f"Buscando en la web datos para '{titulo}'…")
    # tu lógica de requests + BeautifulSoup 
    if titulo in revistas2:
        # Si la revista ya está en el JSON, no la vuelvo a añadir
        print(f"'{titulo}' ya está en el JSON, no se añade de nuevo.")'''



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

def extraer_enlace(url_busqueda):
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
                if enlace:
                    url_extraida = enlace['href']
                    return url_extraida
                else:
                    print("No se encontró el enlace o no tiene atributo href")
                    return None
            else:
                print("No se encontró el div interior")
                return None
        else:
            print("No se encontró el div exterior")
            return None

def extraer_datos_finales(url_final):
    datos_revista = {}
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
                            datos_revista[h2]={}
                            li=div.find_all('li',style='display: inline-block;')
                            for i in li:
                                if i.find('a'):
                                    a=i.find('a').text.strip()
                                    datos_revista[h2][a]=[]
                                    if i.find('ul',class_='treecategory'):
                                        categoria=i.find('ul',class_='treecategory').find_all('li')
                                        for j in categoria:
                                            if j.find('a'):
                                                b=j.find('a').text.strip()
                                                datos_revista[h2][a].append(b)
                        elif h2=="Publisher":
                            datos_revista[h2]=[]
                            p=div.find_all('p')
                            for i in p:
                                if i.find('a'):
                                    a=i.find('a').text.strip()
                                    datos_revista[h2].append(a)
                        elif h2=="SJR 2024":
                            otrah=div.find_all('p')
                            datos_revista["H-Index"]= otrah[1].text.strip()

                        elif h2=="Publication type":
                            datos_revista[h2]=[]
                            p=div.find_all('p')
                            for i in p:
                                    a=i.text.strip()
                                    datos_revista[h2].append(a)
                        
                        elif h2=="ISSN":
                            p=div.find_all('p')
                            for i in p:
                                    a=i.text.strip()
                                    datos_revista[h2]=a
                        elif h2=="Information":
                            p=div.find_all('p')
                            for i in p:
                                    if i.text.strip() =="Homepage":
                                        a=i.find('a')['href']
                                        datos_revista["Homepage"]=a
                    


                            
    return datos_revista
                            
                        


if __name__ == "__main__":
    url = (
        "https://www.scimagojr.com/"
  )
    url_busqueda = (
        "https://www.scimagojr.com/journalsearch.php?q=+"
    )
    palabra="AAC: Augmentative and Alternative Communication"
    nueva_palabra=url_busqueda+palabra.replace(" ", "+").lower()
    palabra_clave=extraer_enlace(nueva_palabra)
    busqueda_maxima=url+palabra_clave
    extraer_datos_finales(busqueda_maxima)