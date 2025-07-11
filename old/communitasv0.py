import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time, random

aux_hom=pd.read_csv('hom_id_isbn.csv',dtype='str')

def obtener_datos(x,df=aux_hom):
    time.sleep(random.uniform(1.5, 4.0))
    '''
    Parte 1 -> Consulta de API
    '''
    # Lista donde se guardara la información
    registro = []
    
    # URL de la API
    api_url = "https://www.communitas.pe/shop/get_product_data"

    # Modificación para asegurar que x sea una cadena o una lista de cadenas
    if isinstance(x, list):
        x = [str(item) for item in x]
    else:
        x = [str(x)]

    # Agrega acá lo solicitado

    x = df[df['isbn'].isin(x)]['id'].tolist()

    if not x:
        print(f"Advertencia: No se encontraron IDs en 'df' para los ISBNs: {x}. Retornando DataFrame vacío.")
        return pd.DataFrame()
    
    # Payload de la API
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "product_ids": x,#[x] if isinstance(x, str) else x, # Si se ingresa solamente un id que lo tome como lista y si se ingresa una lista que tome la lista
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
    
    # Consulta a la API
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    resultado = response.content
    #print(resultado)

    '''
    Parte 2 -> Arreglo de datos, manejo de información
    '''
    # Jsonizado
    api_response = json.loads(resultado.decode('utf-8'))
    
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
    
    data = pd.DataFrame(registro)
    data = data.assign(fecha_consulta=datetime.today())
    return data

df=obtener_datos(9788483933558)
print(df)
#df.to_excel('prueba.xlsx',index=False)