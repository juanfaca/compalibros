import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def obtener_datos(x):
    x=str(x)

    '''
    Parte 1: Construcción de la URL
    '''

    url=f'https://www.crisol.com.pe/catalogsearch/result/?q={x}'
    response=requests.get(url)
    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')
    json_ld_script=soup.find_all('script', type='application/ld+json')[-1]

    '''
    Parte 2: Acomodar los datos
    '''

    df={}
    if json_ld_script:
        # Cargar como JSON
        product_json_data = json.loads(json_ld_script.string)

        # Crear variable nula
        product_price = None

        # Intentar ver el atributo ofertas
        if "offers" in product_json_data and isinstance(product_json_data["offers"], list) and len(product_json_data["offers"]) > 0:
            product_price = product_json_data["offers"][0].get("price")

        sku=product_json_data.get("sku")
        print(f'sku:{sku}')
        print(f'x:{x}')
        if sku!=x:
            df = {
                "nombre": None,
                "marca": None,
                "descripcion": None,
                "precio_venta": None,
                "moneda": None,
                "disponibilidad": "No Disponible",
                "sku": None,
                "gtin": None,
                "url_producto": None
            }
            data = pd.DataFrame([df])
            return data
        else:
            pass
        # Extraer información
        df = {
            "nombre": product_json_data.get("name"),
            "marca": product_json_data.get("brand", {}).get("name"),
            "descripcion": product_json_data.get("description"),
            "precio_venta": product_price,
            "moneda": product_json_data.get("offers", {})[0].get("priceCurrency") if isinstance(product_json_data.get("offers"), list) and len(product_json_data.get("offers")) > 0 else None,
            "disponibilidad": "En Stock" if product_json_data.get("offers") and isinstance(product_json_data.get("offers"), list) and len(product_json_data.get("offers")) > 0 and product_json_data["offers"][0].get("availability") == "https://schema.org/InStock" else "No Disponible",
            "sku": sku,
            "gtin": product_json_data.get("gtin"),
            "url_producto": None if product_json_data.get("url") == "https://www.crisol.com.pe/" else product_json_data.get("url")
        }

    # Crear dataframe con la información
    data = pd.DataFrame([df])
    return data

#df=obtener_datos(9788437648828)
#print(df)