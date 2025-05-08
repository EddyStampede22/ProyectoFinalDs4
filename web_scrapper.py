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
if __name__ == "__main__":
    url = (
        "https://www.scimagojr.com/"
  )
    url_busqueda = (
        "https://www.scimagojr.com/journalsearch.php?q=+"
    )
    palabra="Yi Qi Yi Biao Xue Bao/Chinese Journal of Scientific Instrument"
    nueva_palabra=url_busqueda+palabra.replace(" ", "+").lower()
    print(nueva_palabra)
    palabra_clave=extraer_enlace(nueva_palabra)
    busqueda_maxima=url+palabra_clave
    print(busqueda_maxima)