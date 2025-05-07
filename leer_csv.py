'''Programa para la lectura de archivos CVS y conventirlo en un archivo JSON'''
import os
import pandas as pd
import json
import glob

def crear_diccionario_revistas(carpeta_base):
    """
    Crea un diccionario de revistas leyendo archivos CSV de las subcarpetas 'areas' y 'catalogos'.
    
    Args:
        carpeta_base (str): Ruta a la carpeta base que contiene las subcarpetas 'areas' y 'catalogos'
    
    Returns:
        dict: Diccionario con títulos de revistas como claves y diccionarios de áreas y catálogos como valores
    """
    # Verificar que la estructura de carpetas exista
    carpeta_areas = os.path.join(carpeta_base, 'areas')
    carpeta_catalogos = os.path.join(carpeta_base, 'catalogos')
    
    if not os.path.isdir(carpeta_areas) or not os.path.isdir(carpeta_catalogos):
        raise ValueError(f"Las carpetas 'areas' y 'catalogos' deben existir dentro de {carpeta_base}")
    
    # Leer archivos CSV de áreas
    archivos_areas = glob.glob(os.path.join(carpeta_areas, "*.csv"))
    
    # Diccionario para almacenar la información de revistas
    revistas = {}
    
    # Procesar archivos de áreas
    for archivo in archivos_areas:
        nombre_area = os.path.splitext(os.path.basename(archivo))[0]
        try:
            df = pd.read_csv(archivo, encoding='utf-8')
            # Asumimos que cada archivo tiene una columna con los títulos de revistas
            # Normalizar nombres de revistas (convertir a minúsculas)
            for titulo in df.iloc[:, 0].str.lower():
                if titulo not in revistas:
                    revistas[titulo] = {"areas": [], "catalogos": []}
                # Añadir área a la revista si no está ya
                if nombre_area not in revistas[titulo]["areas"]:
                    revistas[titulo]["areas"].append(nombre_area)
        except Exception as e:
            print(f"Error al procesar el archivo de áreas {archivo}: {e}")
    
    # Procesar archivos de catálogos
    archivos_catalogos = glob.glob(os.path.join(carpeta_catalogos, "*.csv"))
    
    for archivo in archivos_catalogos:
        nombre_catalogo = os.path.splitext(os.path.basename(archivo))[0]
        try:
            df = pd.read_csv(archivo, encoding='utf-8')
            # Normalizar nombres de revistas (convertir a minúsculas)
            for titulo in df.iloc[:, 0].str.lower():
                if titulo not in revistas:
                    # Si la revista aparece en un catálogo pero no en áreas, la creamos
                    revistas[titulo] = {"areas": [], "catalogos": []}
                # Añadir catálogo a la revista si no está ya
                if nombre_catalogo not in revistas[titulo]["catalogos"]:
                    revistas[titulo]["catalogos"].append(nombre_catalogo)
        except Exception as e:
            print(f"Error al procesar el archivo de catálogos {archivo}: {e}")
    
    return revistas

def guardar_como_json(datos, carpeta_destino, nombre_archivo="revistas.json"):
    """
    Guarda un diccionario como archivo JSON.
    
    Args:
        datos (dict): Diccionario a guardar
        carpeta_destino (str): Carpeta donde se guardará el archivo JSON
        nombre_archivo (str): Nombre del archivo JSON
    """
    # Crear la carpeta de destino si no existe
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Ruta completa del archivo
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    
    # Guardar como JSON con formato legible
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print(f"Archivo JSON guardado exitosamente en: {ruta_archivo}")

def main():
    # Carpeta base donde se encuentran las subcarpetas 'areas' y 'catalogos'
    carpeta_base = "datos\csv"  # Cambia esto a la ruta de tu carpeta base
    
    # Carpeta de destino para el archivo JSON
    carpeta_json = "datos\json"  # Cambia esto a la ruta de tu carpeta de destino
    
    try:
        # Crear el diccionario de revistas
        print("Procesando archivos CSV...")
        revistas = crear_diccionario_revistas(carpeta_base)
        
        # Mostrar estadísticas
        print(f"\nEstadísticas:")
        print(f"- Total de revistas procesadas: {len(revistas)}")
        areas_por_revista = {titulo: len(info["areas"]) for titulo, info in revistas.items()}
        catalogos_por_revista = {titulo: len(info["catalogos"]) for titulo, info in revistas.items()}
        
        if areas_por_revista:
            print(f"- Promedio de áreas por revista: {sum(areas_por_revista.values()) / len(areas_por_revista):.2f}")
        if catalogos_por_revista:
            print(f"- Promedio de catálogos por revista: {sum(catalogos_por_revista.values()) / len(catalogos_por_revista):.2f}")
        
        # Mostrar ejemplo de algunas revistas
        print("\nEjemplos de revistas procesadas:")
        for i, (titulo, info) in enumerate(list(revistas.items())[:3]):
            print(f"  {i+1}. '{titulo}': {info}")
        
        # Guardar como JSON
        guardar_como_json(revistas, carpeta_json)
        
    except Exception as e:
        print(f"Error en el procesamiento: {e}")

if __name__ == "__main__":
    main()