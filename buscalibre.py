import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def obtener_datos(x):
    x=str(x)

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    '''
    Parte 1: Construcción de la URL
    '''

    url=f'https://www.buscalibre.pe/libros/search/?q={x}'
    response = session.get(url, headers=headers)
    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')

    # Buscar el script con tipo "Product"
    product_data = None
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "Product":
                        product_data = item
            elif data.get("@type") == "Product":
                product_data = data
        except json.JSONDecodeError:
            continue

    # Extraer información
    if product_data:
        # Obtener todas las ofertas y elegir la más barata
        offers = product_data.get("offers", [])
        if isinstance(offers, dict):  # si solo hay una oferta
            best_offer = offers
        elif isinstance(offers, list) and offers:
            best_offer = min(offers, key=lambda x: float(x.get("price", float("inf"))))
        else:
            best_offer = {}

        row = {
            "url_producto": product_data.get("url"),
            "url_imagen": product_data.get("image"),
            "nombre": product_data.get("name"),
            "isbn": product_data.get("isbn"),
            "autor": product_data.get("author", {}).get("name"),
            "editorial": product_data.get("publisher", {}).get("name"),
            "precio_venta": best_offer.get("price"),
            "condicion": best_offer.get("itemCondition"),
            "disponibilidad": best_offer.get("availability")
        }

        # Crear DataFrame
        data = pd.DataFrame([row])
        return data
    else:
        print("No se encontró información de producto.")

df=obtener_datos(9788489693210)
print(df)