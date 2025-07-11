import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def obtener_datos(x):

    x=str(x)
    '''
    Parte 1: Con ISBN ingresado se consigue la url del libro
    '''
    base='https://www.iberolibrerias.com'
    url=base+'/'+x+'?_q='+x+'&map=ft'

    response=requests.get(url)
    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')

    hrefs=[]
    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        if href:  # Ensure the 'href' attribute actually exists
            hrefs.append(href)
    referencia = next(filter(lambda id: any(sub in id for sub in x) and 'https' not in id, hrefs))
    enlace=base+referencia

    '''
    Parte 2: Con al url obtenida, se busca la id interna del libro
    '''
    response=requests.get(enlace)

    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')

    meta_tag = soup.find('meta', attrs={'property': 'product:retailer_part_no'})
    id = meta_tag['content'] if meta_tag else None

    '''
    Parte 3: Con el id se consulta la API
    '''

    api_url = (
        f"https://www.iberolibrerias.com/_v/segment/routing/vtex.store@2.x/product/"
        f"{id}/product-details/p"
    )

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.iberolibrerias.com/"
    }

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    html_content = response.content.decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    json_ld_script = soup.find('script', type='application/ld+json')


    df = {}
    if json_ld_script:
        # Cargar el contenido del script como JSON
        data = json.loads(json_ld_script.string)
        #print(data)
        # Inicializar el precio en caso de que no se encuentre
        extracted_price = None

        # Intentar obtener el precio de la primera oferta específica
        if "offers" in data and "offers" in data["offers"] and isinstance(data["offers"]["offers"], list) and len(data["offers"]["offers"]) > 0:
            extracted_price = data["offers"]["offers"][0].get("price")

        # Extraer la información relevante
        df = {
            "nombre": data.get("name"),
            "marca": data.get("brand", {}).get("name"),
            "descripcion": data.get("description"),
            "precio_venta": extracted_price,  # Usamos el precio extraído directamente
            "moneda": data.get("offers", {}).get("priceCurrency"),
            "disponibilidad": "En Stock" if data.get("offers", {}).get("offers") and data["offers"]["offers"][0].get("availability") == "http://schema.org/InStock" else "No Disponible",
            "sku": data.get("sku"),
            "gtin": data.get("gtin"),
            "url_producto":enlace
        }
    else:
            df = {
            "nombre": None,
            "marca": None,
            "descripcion": None,
            "precio_venta": None,  # Usamos el precio extraído directamente
            "moneda": None,
            "disponibilidad": "No Disponible",
            "sku": None,
            "gtin": None,
            "url_producto":None
        }

    # Crear un DataFrame de pandas con la información extraída
    data = pd.DataFrame([df])

    return data

df=obtener_datos(9788495359476)
print(df)