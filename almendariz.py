from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime


def getPrice(string):
    index = string.index(r'<\/bdi>')
    string = string.replace(string[index::],'')
    string = re.search('[0-9]+.[0-9]+', string).group()
    return string


def hasOffer(string):
    if string.count('S/') > 1:
        return True
    else:
        return False


searchPrice = lambda string: re.search(r'S/\s[0-9]+.[0-9]+', string).group()


getVolume = lambda string: re.search(r'([0-9]+(|\s)(ml|ML|l|L))', string).group()


printDate = lambda: f'{datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} {datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}'


def WebScraping(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
    }
    
    request_obtained = requests.get(url, headers=headers)
    html_obtained = request_obtained.text
    soup = BeautifulSoup(html_obtained, 'html.parser')

    products_name = soup.find_all('h2', {'class': 'woocommerce-loop-product__title'})
    products_price = soup.find_all('span', {'class': 'price'})

    names = []
    normal_prices = []
    offer_prices = []
    volumes = []
    dates = []

    for i in range(len(products_name)):
        names.append(products_name[i].text)

        if hasOffer(products_price[i].text) == True:
            normal_prices.append(searchPrice(products_price[i].text))
            offer_price = products_price[i].text.replace(searchPrice(products_price[i].text),'')
            offer_prices.append(searchPrice(offer_price))
        else:
            normal_prices.append(searchPrice(products_price[i].text))
            offer_prices.append('')


        dates.append(printDate())

    for i in names:
        try:
            volumes.append(getVolume(i))
        except:
            volumes.append('')
    return dates, names, normal_prices, offer_prices, volumes


def create_dataset(columns, data):
    df = pd.DataFrame(columns=columns)
    j = 0
    for i in columns:
        df[i] = data[j]
        j += 1
    return df


url_almendariz = 'https://almendariz.com.pe/categoria-producto/'

url_liquors = ['whisky', 'ron', 'vodka', 'tequilas', 'gin', 'piscos', 'vinos', 'burbujas', 'aguas-energizantes', 'cervezas', 'licores-spirits']
liquors_name = ['Whisky', 'Ron', 'Vodka', 'Tequila', 'Gin', 'Pisco', 'Vino', 'Burbujas', 'Aguas y energizantes', 'Cerveza', 'Licores y spirits']
dates, names, normal_prices, offer_prices, volumes, categories  = [], [], [], [], [], []


for i in range(len(url_liquors)):
    print(f'Obteniendo la data de la siguiente categoría: {liquors_name[i]}')
    url_almendariz += url_liquors[i]
    dates2, names2, normal_prices2, offer_prices2, volumes2 = WebScraping(url_almendariz)
    dates += dates2
    names += names2 
    normal_prices += normal_prices2
    offer_prices += offer_prices2
    volumes += volumes2
    categories2 = [liquors_name[i] for k in range(len(names2))]
    categories += categories2
    url_almendariz = 'https://almendariz.com.pe/categoria-producto/'


columns = ['Fecha de consulta', 'Nombre del producto', 'Precio normal', 'Precio de oferta', 'Cantidad', 'Categoría']
data = [dates, names, normal_prices, offer_prices, volumes, categories]
df = create_dataset(columns, data)

file_name = f'Almendariz - {datetime.datetime.now().day}-{datetime.datetime.now().month}-{datetime.datetime.now().year}.xlsx'
df.to_excel(file_name, index=False)

print(f'Consulta realizada el {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} a las {datetime.datetime.now().hour}:{datetime.datetime.now().minute}')