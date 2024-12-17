from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime


searchPrice = lambda string: re.search(r'S/.\s[0-9]+.[0-9]+', string).group()


getVolume = lambda string: re.search(r'([0-9]+(|\s)(ml|ML|l|L))', string).group()


getNumber = lambda string: re.search(r'[0-9]+', string).group()


printDate = lambda: f'{datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} {datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}'


def WebScraping(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    request_obtained = requests.get(url, headers=headers)
    html_obtained = request_obtained.text
    soup = BeautifulSoup(html_obtained, 'html.parser')

    title = soup.find('title')
    products_scraping = soup.find_all('div', {'class': 'product-item-meta'})
    products_number = soup.find('span', {'class': 'product-facet__meta-bar-item product-facet__meta-bar-item--count'}).text

    names = []
    normal_prices = []
    offer_prices = []
    volumes = []
    dates = []

    for product in products_scraping:
        name = product.a.text
        prices = product.find_all('span')
        if len(prices) == 2:
            normal_price = searchPrice(prices[0].text)
            offer_price = ''
        if len(prices) == 4:
            normal_price = searchPrice(prices[2].text)
            offer_price = searchPrice(prices[0].text)

        names.append(name)
        normal_prices.append(normal_price)
        offer_prices.append(offer_price)
        dates.append(printDate())
    
    for i in names:
        try:
            volumes.append(getVolume(i))
        except:
            volumes.append('')

    # columns = ['Nombre', 'Precio', 'Tipo', 'Negocio']

    return dates, names, normal_prices, offer_prices, volumes, products_number


def create_dataset(columns, data):
    df = pd.DataFrame(columns=columns)
    j = 0
    for i in columns:
        df[i] = data[j]
        j += 1
    return df


url_LU = 'https://licoreriasunidas.pe/collections/'
url_liquors = ['whiskies', 'ron', 'espumantes', 'gin', 'vodka', 'vinos-nacionales', 'pisco', 'tequila']
liquors_name = ['Whisky', 'Ron', 'Espumante', 'Gin', 'Vodka', 'Vino', 'Pisco', 'Tequila']
dates, names, normal_prices, offer_prices, volumes, categories  = [], [], [], [], [], []
previous_names_quantity = 0

columns = ['Fecha de consulta', 'Nombre del producto', 'Precio normal', 'Precio de oferta', 'Cantidad', 'Categoría']
df = pd.DataFrame(columns=columns)

for i in range(len(url_liquors)):
    print(f'Obteniendo la data de la siguiente categoría: {liquors_name[i]}')
    url_LU += url_liquors[i]
    dates2, names2, normal_prices2, offer_prices2, volumes2, products_number = WebScraping(url_LU)
    dates += dates2
    names += names2
    normal_prices += normal_prices2
    offer_prices += offer_prices2
    volumes += volumes2
    products_number = getNumber(products_number)
    categories2 = [liquors_name[i] for k in range(int(products_number))]

    j = 2
    while len(names) - previous_names_quantity != int(products_number):
        url_LU2 = url_LU
        url_LU += '?page=' + str(j)
        j += 1
        dates2, names2, normal_prices2, offer_prices2, volumes2, products_number = WebScraping(url_LU)
        dates += dates2
        names += names2 
        normal_prices += normal_prices2
        offer_prices += offer_prices2
        volumes += volumes2
        products_number = getNumber(products_number)
        url_LU = url_LU2
    previous_names_quantity = len(names)
    categories += categories2
    url_LU = 'https://licoreriasunidas.pe/collections/'

data = [dates, names, normal_prices, offer_prices, volumes, categories]

df_LU = create_dataset(columns, data)

file_name = f'Licorerías Unidas - {datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}.xlsx'
df_LU.to_excel(file_name, index=False)
print(f'Consulta realizada el {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} a las {datetime.datetime.now().hour}:{datetime.datetime.now().minute}')