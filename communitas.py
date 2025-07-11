import cloudscraper
import re
import json
from bs4 import BeautifulSoup
import pandas as pd

def obtener_datos(x):
    '''
    Parte 1 -> Obteniendo ID en base al ISBN
    '''

    x=str(x)
    # Scraper para saltar cloudfare
    scraper = cloudscraper.create_scraper(
        delay=10,
        browser={'browser': 'chrome','platform': 'windows','mobile': False}
    )
    url = f'https://www.communitas.pe/shop?search={x}'

    # Parseo del html y extracción de información
    response = scraper.get(url)
    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')

    # Se encuentra el ID
    #ids = [btn['data-product-product-id'] for btn in soup.find_all('button', attrs={"data-product-product-id": True})]
    try:
        id = soup.find('button', attrs={"data-product-product-id": True})['data-product-product-id']
    except:
        aux = {
        "id": None,
        "nombre": None,
        "nombre_auxiliar": None,
        "url_imagen": None,
        "url_producto": None,
        "precio_lista": None,
        "precio_venta": None,
        "ids_categorias": None,
        "disponibilidad": "No Disponible"
    }
        data = pd.DataFrame([aux])
        return data
    #print(id)
    '''
    Parte 2 -> Consulta de API de precios e información
    '''
    # Lista donde se guardara la información
    registro = []
    
    # URL de la API
    api_url = "https://www.communitas.pe/shop/get_product_data"
    
    # Payload de la API
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_ids": [id],
            "cookies": []
        },
        "id": 1 # Me parece que no importa
    }
    
    # Encabezados de la API
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.communitas.pe/shop/"
    }

    # Reinicio del scraper

    scraper = cloudscraper.create_scraper(
        delay=10,
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    # Consulta a la API
    response = scraper.post(api_url, headers=headers, data=json.dumps(payload))
    resultado = response.content
    #print(resultado)

    '''
    Parte 3 -> Arreglo de datos, manejo de información
    '''
    # Jsonizado
    api_response = json.loads(resultado.decode('utf-8'))
    #print(api_response)
    
    # Base URL para las imágenes y enlaces de productos
    base_domain = "https://www.communitas.pe"

    # Iterar sobre cada ID de producto en la respuesta
    # La API devuelve los datos de los productos como claves directas bajo 'result'
    # Excluimos 'cookies' ya que no es información de un producto individual
    for product_id_key, product_data_fragment in api_response.get('result', {}).items():
        if product_id_key == 'cookies':
            continue # Saltar la clave 'cookies'

        # Datos del producto
        product_id = product_data_fragment['product']['id']
        product_name = product_data_fragment['product']['name']
        product_display_name = product_data_fragment['product']['display_name']
        
        # Parseo para manejar más información
        soup = BeautifulSoup(product_data_fragment['render'], 'html.parser')
        
        # Data de imágenes
        img_tag = soup.find('img', class_='o_image_64_max')
        image_url = base_domain + img_tag.get('src', '') if img_tag else None
        
        # URL del producto
        product_link_tag = soup.find('h6').find('a') if soup.find('h6') else None
        product_url = base_domain + product_link_tag.get('href', '') if product_link_tag else None
        
        # Precios
        list_price_tag = soup.find('del', class_='text-danger')
        sale_price_tag = soup.find('span', attrs={"data-oe-expression": "combination_info['price']"})
        
        list_price = float(list_price_tag.find('span', class_='oe_currency_value').text.replace(',','')) if list_price_tag and list_price_tag.find('span', class_='oe_currency_value') else None
        sale_price = float(sale_price_tag.find('span', class_='oe_currency_value').text.replace(',','')) if sale_price_tag and sale_price_tag.find('span', class_='oe_currency_value') else None

        # Miscelánea
        #category_ids = json.loads(soup.find('div', class_='o_product_row')['data-category_ids']) if soup.find('div', class_='o_product_row') else []
        
        category_ids = []
        div_producto = soup.find('div', class_='o_product_row')

        if div_producto and div_producto.get('data-category_ids'):
            category_ids = json.loads(div_producto.get('data-category_ids'))
        
        # Consolidado
        aux = {
            "id": product_id, # Usar el product_id real del diccionario, no 'x'
            "nombre": product_name,
            "nombre_auxiliar": product_display_name,
            "url_imagen": image_url,
            "url_producto": product_url,
            "precio_lista": list_price,
            "precio_venta": sale_price,
            "ids_categorias": category_ids
        }
        registro.append(aux)

    #print(product_url)
    match = re.search(r'-([0-9]+)(?=#)', product_url)
    id_raro = match.group(1)
    #print(id_raro)

    '''
    Adicional: Consulta a la API de disponibilidad de producto
    '''

    # URL de la API
    api_url = "https://www.communitas.pe/sale/get_combination_info_website"
    
    # Payload de la API
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_template_id": id_raro,
            "product_id": id,
            "combination": [],#[784609, 784606, 784613, 784607, 784610, 832635, 784612, 784608, 784611],
            "parent_combination": [],
            "add_qty": 1,
            "pricelist_id": False
        },
        "id": 1
    }

    # Reinicio del scraper

    scraper = cloudscraper.create_scraper(
        delay=10,
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    # Consulta a la API
    response = scraper.post(api_url, headers=headers, data=json.dumps(payload))
    data = response.json()
    print(data)
    stock = data['result']['available_threshold']
    print(stock)
    if stock>0:
        dis='En Stock'
    else:
        dis='No Disponible'

    # Finalmente se agrega la disponibilidad

    registro[-1]["disponibilidad"] = dis
    
    data = pd.DataFrame(registro)
    return data

#df=obtener_datos(9788483930250)
#print(df)