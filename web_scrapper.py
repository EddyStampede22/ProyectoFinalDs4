''' Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior, buscará información de cada revista en SCIMAGO 
y la guardará en un nuevo archivo JSON'''
# importar las librerías necesarias
import json
import os
import requests
from bs4 import BeautifulSoup
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

def obtener_Html(titulo):
    """
    Función para obtener el HTML de una página web.
    
    Args:
        titulo (str): Título del libro o revista.
    
    Returns:
        str: HTML de la página web.
    """
    # Aquí iría tu lógica para obtener el HTML de la página web
    # Por ejemplo, usando requests y BeautifulSoup
    pass

revistas = leer_json_seguro("revis.json")  # libros es un dict: {titulo: {...}, ...}
revistas2 = leer_json_seguro("revistas.json") # libros es un dict: {titulo: {...}, ...}

for titulo in revistas:
    # aquí 'titulo' es ya la clave (el nombre del libro)
    info = revistas[titulo]  # p. ej. {'autor': ..., 'año': ...}
    print(f"Buscando en la web datos para '{titulo}'…")
    # tu lógica de requests + BeautifulSoup 
    if titulo in revistas2:
        # Si la revista ya está en el JSON, no la vuelvo a añadir
        print(f"'{titulo}' ya está en el JSON, no se añade de nuevo.")