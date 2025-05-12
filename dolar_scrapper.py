'''
Dolar Scrapper
'''
import requests
from bs4 import BeautifulSoup

def scrap(url:str):
    ''' Obtiene página desde Internet'''
    pagina = requests.get(url,timeout=10)
    return pagina
 
def get_exchange_rate(dom):
    exchange_rates = {}
    for row in dom.find_all('p'):
        print(f"{row}")
        title = row.text.strip()
        if title[0] == 'C':
            title = 'Compra'
        else:
            title = 'Venta'
        value = row.find('span')
        value = value.text.strip()
        exchange_rates[title] = value #actualizamos dict
    return exchange_rates

def main():
    url = 'https://www.eldolar.info/es-MX/mexico/dia/hoy'
    pagina = scrap(url)
    soup = BeautifulSoup(pagina.content,"html.parser")
    #result = soup.find(class_="exchangeRate")
    #ex = get_exchange_rate(result)
    table = soup.find(id='dllsTable')
    d = get_exchange_rate_dict(table)
    #imprimimos las instituciones y sus valores
    for k,v in d.items():
        print(k,v)
 
def update_with_5_columns(dictionary, columns):
    i = 0
    for col in columns:
        if i == 0:
            institucion = col.find(class_='small-hide')
            institucion = institucion.text.strip()
            #print(institucion)
        if i == 3:
            compra = col.text.strip()
            compra = float(compra)
            #print(compra)
        if i == 4:
            venta = float(col.text.strip())
            #print(venta)
            d = {'compra':compra,'venta':venta}
            dictionary[institucion] = d
        i+=1

def get_exchange_rate_dict(dom):
    dictionary = {}
    body = dom.find('tbody')
    for row in body.find_all('tr'):
        columns = row.find_all('td')
        if (len(columns) == 4):
            update_with_4_columns(dictionary,columns)
        if (len(columns) == 5):
            update_with_5_columns(dictionary,columns)
    return dictionary
 
def update_with_4_columns(dictionary, columns):
    i = 0
    for col in columns:
        if i == 0:
            institucion = col.find(class_='small-hide')
            institucion = institucion.text.strip()
            #print(institucion)
        if i == 3:
            fix = float(col.text.strip())
            #print(fix)
            d = {'fix':fix}
            dictionary[institucion] = d
        i+=1
 
if __name__ == "__main__":
    main()