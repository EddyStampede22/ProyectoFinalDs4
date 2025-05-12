# Proyecto Final Desarrollo 4 (2pm-3pm)
## El proyecto consta de 3 partes:
### 1. Un programa que lea varios archivos CSV y genere un archivo JSON para ser usado por las siguientes partes
### 2. Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior y buscará información de cada revista en SCIMAGO y la guardará en un nuevo archivo JSON
### 3 Un programa front-end que leerá este último archivo JSON y permitirá navegar sus contenidos por Catálogo, por Área y por búsqueda de título
### Actualización: aquí solo se mostrará las instrucciones de los programas del punto 1 y 2.
## Integrantes
### Martinez Pimbert Jose Eduardo

# Instrucciones:
## Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

1. Python 3.6 o superior
2. Las siguientes bibliotecas de Python:
   ```
   pip install pandas requests beautifulsoup4 chardet
   ```

## Estructura de directorios

El sistema espera la siguiente estructura de directorios:

```
proyecto/
├── leer_csv.py
├── web_scrapper_mejorado.py
├── datos/
│   ├── csv/
│   │   ├── areas/
│   │   │   └── [archivos CSV de áreas]
│   │   └── catalogos/
│   │       └── [archivos CSV de catálogos]
│   └── json/
│       ├── cache/
│       │   └── [aquí se guardarán los archivos de caché]
│       ├── revistas.json (se generará)
│       ├── revistas_scimago_final.json (se crea vació y después el programa lo actualizará finalizando)
│   	├── scrapping.log (se generará)
        └── ultimo_procesado.txt (se generará)
```

## Paso 1: Preparación de los archivos CSV y estructura de directorios

1. Crea la estructura de directorios mencionada arriba.
2. Coloca los archivos CSV (que se encuentran en el repositorio) en las carpetas correspondientes:
   - En `datos/csv/areas/` 
   - En `datos/csv/catalogos/`
3. Crea una carpeta `cache` dentro de `datos/json/` para almacenar los archivos de caché.
(si no la creas, el programa se encargará de crearla)
4. Crea un archivo vacío llamado `revistas_scimago_final.json` dentro de la carpeta `datos/json/`. Este archivo es necesario para que el programa web scraper funcione correctamente.

**Nota importante:** Cada archivo CSV debe tener el nombre del área o catálogo. Por ejemplo, `MEDICINA.csv` o `SCOPUS.csv`. El programa utilizará el nombre del archivo como identificador.

## Paso 2: Ejecución del primer programa (leer_csv.py)

Este programa lee los archivos CSV y genera un archivo JSON con la información consolidada.

1. Abre una terminal o línea de comandos.
2. **Importante:** Navega hasta la carpeta `datos/json/` del proyecto.
   ```
   cd ruta/al/proyecto/datos/json/
   ```
3. Ejecuta el primer programa (indicando la ruta para acceder al archivo):
   ```
   python ../../leer_csv.py
   ```
   o si estás en Windows:
   ```
   python ..\..\leer_csv.py
   ```
4. El programa generará un archivo `revistas.json` en la carpeta `datos/json/` (carpeta actual).

## Paso 3: Ejecución del segundo programa (web_scrapper_mejorado.py)

Este programa lee el archivo JSON generado, busca información adicional en SCIMAGO para cada revista y guarda los resultados en un nuevo archivo JSON.

1. Asegúrate de que el archivo `revistas.json` se haya generado correctamente en la carpeta `datos/json/` (carpeta actual).
2. Verifica que existe el archivo vacío `revistas_scimago_final.json` en la carpeta `datos/json/` (carpeta actual). Si no existe, créalo.
3. **Importante:** Mantente en la carpeta `datos/json/` para ejecutar este programa:
   ```
   python ../../web_scrapper_mejorado.py
   ```
   o si estás en Windows:
   ```
   python ..\..\web_scrapper_mejorado.py
   ```
4. El programa utilizará `revistas_scimago_final.json` en la carpeta `datos/json/` (carpeta actual) para guardar toda la información obtenida de SCIMAGO.

**Nota:** Si por ejemplo te quedaste en el archivo parcial `revistas_scimago_parcial_12000.json`, puedes cambiarle el nombre a 
`revistas_scimago_final.json` y eliminar el otro `revistas_scimago_final.json` vació porque cuando continues no va unir toda la información ya que como el programa no finalizó, cuando lo vuelvas a correr y finalize, se unirá los datos con `revistas_scimago_final.json` vació y no con `revistas_scimago_parcial_12000.json`. Asi que, puedes cambiar el nombre al archivo parcial o bien poner el nombre del archivo parcial en la parte final del main en el programa `web_scrapper_mejorado.py`:
```python
# Guardar resultados finales
    if resultados:
        # Combinar con el catálogo existente
        catalogo_actualizado = {**catalogo, **resultados}
        leer_csv.guardar_como_json(catalogo_actualizado, "revistas_scimago_final.json")
        logging.info(f"Proceso completado. Revistas encontradas: {contador['encontrados']}")
        logging.info(f"Revistas no encontradas: {contador['no_encontrados']}")
    else:
        logging.info("No se encontraron revistas nuevas")
```

**Nota:** El web scraper utiliza un sistema de caché para evitar solicitudes repetidas. Los archivos de caché se guardan en la carpeta `datos/json/cache/` (subcarpeta de la carpeta actual). Si necesitas volver a realizar la búsqueda para alguna revista, elimina los archivos correspondientes de esta carpeta antes de ejecutar el programa. O puedes eliminar el archivo ultimo_procesado.txt

## Comportamiento y características

### Programa leer_csv.py

- Lee archivos CSV con diferentes codificaciones (UTF-8, Latin1, ISO-8859-1, etc.)
- Normaliza los nombres de revistas (convierte a minúsculas)
- Clasifica las revistas por áreas y catálogos
- Guarda los resultados en formato JSON

### Programa web_scrapper_mejorado.py

- Utiliza multithreading para realizar consultas en paralelo (5 hilos por defecto)
- Implementa técnicas anti-bloqueo (esperas aleatorias, cabeceras de navegador)
- Guarda resultados parciales cada 200 revistas procesadas
- Mantiene un registro de la última revista procesada para poder continuar en caso de interrupción
- Almacena información detallada sobre cada revista:
  - Áreas temáticas y categorías
  - Editorial
  - Índice H
  - Tipo de publicación
  - ISSN
  - Página web
  - Información para widget (Imagen y código HTML)

## Solución de problemas

### Errores de ruta o archivo no encontrado

- Asegúrate de ejecutar los programas desde la carpeta `datos/json/` como se indica en las instrucciones
- Verifica que la estructura de directorios sea exactamente la indicada
- Comprueba que existe el archivo vacío `revistas_scimago_final.json` antes de ejecutar el web scraper

### El programa no encuentra algunas revistas en SCIMAGO

- Esto es normal ya que no todas las revistas están indexadas en SCIMAGO
- Revisa el archivo `scraping.log` para ver qué revistas no se encontraron
- Puedes revisar el último titulo generado por el último archivo generado parcialmente e insertar ese nombre en ultimo_procesado.txt

### El programa se detiene o es bloqueado por SCIMAGO

- El programa está diseñado para continuar desde donde se quedó, siempre y cuando, se conserve el caché y el ultimo_procesado.txt
- Reduce el número de trabajadores concurrentes modificando la variable `num_trabajadores` en el archivo `web_scrapper_mejorado.py`
- Aumenta los tiempos de espera aleatorios en la función `get_soup`

### Errores de codificación en los archivos CSV

- El programa intenta detectar automáticamente la codificación
- Si hay problemas, puedes editar manualmente el archivo CSV y guardarlo con codificación UTF-8

### Otros detalles
- También puedes cambiar el número de revistas para guardar el archivo parcial 


### - Nota: Para este proyecto se utlizaron Asistentes Digitales (ChatGTP, Claude)
