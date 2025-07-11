import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def obtener_datos(x):
    '''
    Parte 1: Encontrar la URL con el ISBN
    '''
    x=str(x)
    base='https://www.elvirrey.com/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda='
    url=base+x

    response=requests.get(url)
    byte_content=response.content
    html_string = byte_content.decode('utf-8')
    soup = BeautifulSoup(html_string, 'html.parser')

    # Encontrar la url
    dls=soup.find_all('dl')
    for dl in dls:
        a_tag = dl.find('a')
        if a_tag and 'href' and 'data-id' in a_tag.attrs:
            referencia=a_tag['href']
            #id=a_tag['data-id']
    try:    
        url='https://www.elvirrey.com'+referencia
    except:
        product_data = {
            "nombre": None,
            "autor": None,
            "marca": None,
            "descripcion": None,
            "precio_venta": None,  # Usamos el precio extraído directamente
            "moneda": None,
            "disponibilidad" : "No Disponible",
            "url_producto": None
        }
        data = pd.DataFrame([product_data])
        return data

    '''
    Parte 2: Acceso al html de la página
    '''
    response=requests.get(url)
    html_content = response.content.decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')

    json_ld_script = soup.find_all('script', type='application/ld+json')[-1]

    product_data = {}
    if json_ld_script:
        # Cargar el contenido del script como JSON
        data = json.loads(json_ld_script.string)

        # Inicializar el precio en caso de que no se encuentre
        extracted_price = None

        # Intentar obtener el precio de la primera oferta específica
        extracted_price = data["offers"].get("price")
        #print(type(extracted_price))

        # Extraer la información relevante
        product_data = {
            "nombre": data.get("name"),
            "autor":data.get('author'),
            "marca": data.get('publisher'),
            "descripcion": data.get("description"),
            "precio_venta": extracted_price,  # Usamos el precio extraído directamente
            "moneda": data.get("offers", {}).get("priceCurrency"),
            "disponibilidad" : "En Stock" if data["offers"].get("availability") == "http://schema.org/InStock" else "No Disponible",
            "url_producto":url
        }

    # Crear un DataFrame de pandas con la información extraída
    data = pd.DataFrame([product_data])
    return data

df=obtener_datos(9788437648828)
print(df)