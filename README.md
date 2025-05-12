# Proyecto Final Desarrollo 4 (2pm-3pm)
## El proyecto que consta de 3 partes:
### 1. Un programa que lea varios archivos CSV y genere un archivo JSON para ser usado por las siguientes partes
### 2. Un programa "web scrapper" que leerá el archivo JSON generado por la parte anterior y buscará información de cada revista en SCIMAGO y la guardará en un nuevo archivo JSON
### 3 Un programa front-end que leerá este último archivo JSON y permitirá navegar sus contenidos por Catálogo, por Área y por búsqueda de título
### Actualización: aquí solo se mostrará las instrucciones de los programas del punto 1 y 2.
## Integrantes
### Martinez Pimbert Jose Eduardo

# Instrucciones
### El repositorio incluye dos programas: 
## 1.- leer_csv.py 
### se encargará de leer los archivos csv que se encuentran en la carpeta datos\cvs y juntarlos en un diccionario donde la clave será el titulo y los valores estarán 

## 2.- web_scapper_mejorado
### Con la información obtenida del JSON del anterior programa, el programa tomará la tarea de extraer ciertos datos de la página {aqui va la pagina} utilizando las llaves (titulos de las revistas). El programa se descompone a partir de sus principales funciones:
### 