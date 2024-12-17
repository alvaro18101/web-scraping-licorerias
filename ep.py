from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
import re
import pandas as pd
import datetime


getVolume = lambda string: re.search(r'([0-9]+(|\s)(ml|ML|l|L))', string).group()


printDate = lambda: f'{datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} {datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}'


getMaxPage = lambda string: re.search(r'[0-9]+', string).group()

# Configurar opciones para ejecutar Chrome en segundo plano
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')


def WebScraping(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(200,200)
    driver.get(url)

    # Esperar un momento para que se cargue todo el contenido dinámico
    time.sleep(5)  # Ajusta el tiempo según sea necesario

    # Extraer el HTML completo de la página renderizada
    html = driver.page_source

    # Cerrar el navegador
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    products = soup.find_all('div', {'class': 'sc-hZNxer bMLimf'})
    max_page = soup.find('div', {'class': 'sc-leiOXd botggN'}).p.text

    names = []
    normal_prices = []
    offer_prices = []
    volumes = []
    dates = []

    for element in products:
        names.append(element.find('p', {'class': 'sc-hLBbgP dwTaqX'}).text)
        try:
            normal_prices.append(element.find('p', {'class': 'sc-hLBbgP hIScDW'}).text)
            offer_prices.append(element.find('p', {'class': 'sc-hLBbgP hRsqvU'}).text)
        except:
            normal_prices.append(element.find('p', {'class': 'sc-hLBbgP hRsqvU'}).text)
            offer_prices.append('')
        
        dates.append(printDate())

    for i in names:
        try:
            volumes.append(getVolume(i))
        except:
            volumes.append('')

    return dates, names, normal_prices, offer_prices, volumes, int(getMaxPage(max_page))


def create_dataset(columns, data):
    df = pd.DataFrame(columns=columns)
    j = 0
    for i in columns:
        df[i] = data[j]
        j += 1
    return df


url = "https://elpozito.com.pe/el-pozito?category="
url_liquors = ['vinos', 'pisco', 'ron', 'tequila%20y%20mezcal', 'whisky', 'gin', 'vodka', 'burbujas', 'licores%20y%20spirits', 'cervezas', 'aguas%20y%20energizantes']
liquors_name = ['Vino', 'Pisco', 'Ron', 'Tequila y Mezcal', 'Whisky', 'Gin', 'Vodka', 'Burbujas', 'Licores y Spirits', 'Cerveza', 'Aguas y Energizantes']
dates, names, normal_prices, offer_prices, volumes, categories  = [], [], [], [], [], []

for i in range(len(url_liquors)):
    print(f'Obteniendo la data de la siguiente categoría: {liquors_name[i]}')
    url += url_liquors[i]
    dates2, names2, normal_prices2, offer_prices2, volumes2, max_page = WebScraping(url)
    dates += dates2
    names += names2
    normal_prices += normal_prices2
    offer_prices += offer_prices2
    volumes += volumes2
    categories2 = [liquors_name[i] for k in range(len(names2))]
    categories += categories2
    # Scraping en la página 2, 3, ...
    page_number = 2
    while page_number <= max_page:
        url2 = url
        url += '&page=' + str(page_number)
        page_number += 1
        dates2, names2, normal_prices2, offer_prices2, volumes2, max_page = WebScraping(url)
        dates += dates2
        names += names2 
        normal_prices += normal_prices2
        offer_prices += offer_prices2
        volumes += volumes2
        categories2 = [liquors_name[i] for k in range(len(names2))]
        categories += categories2
        url = url2

    url = "https://elpozito.com.pe/el-pozito?category="

columns = ['Fecha de consulta', 'Nombre del producto', 'Precio normal', 'Precio de oferta', 'Cantidad', 'Categoría']

data = [dates, names, normal_prices, offer_prices, volumes, categories]

# Guardar o procesar los datos
df = create_dataset(columns, data)
file_name = f'El Pozito - {datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}.xlsx'
df.to_excel(file_name, index=False)

print(f'Consulta realizada el {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} a las {datetime.datetime.now().hour}:{datetime.datetime.now().minute}')