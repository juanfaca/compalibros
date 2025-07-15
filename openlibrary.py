import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def obtener_datos(x):
    x=str(x)
    url=f'https://openlibrary.org/isbn/{x}.json'
    response=requests.get(url)
    if response.status_code==200:
        info=response.json()
        #print(info)
        nombre=info.get('title') #
        fec_publicacion=info.get('publish_date') #
        try:
            lista_eds=info.get('publishers')
            if len(lista_eds)>1:
                for i in lista_eds:
                    editorial=editorial+', '+i
                editorial=editorial[2:]
            else:
                editorial=lista_eds[0]
        except:
            editorial=''
        try:
            descripcion = info.get('description').get('value')
            if descripcion is None:
                descripcion = ''
        except:
            descripcion = ''
        try:
            formato = info.get('physical_format')
            if formato is None:
                formato = ''
        except:
            paginas = ''
        try:
            paginas = info.get('number_of_pages')
            if paginas is None:
                paginas = ''
        except:
            paginas = ''
        try:    
            id_imagen=info.get('covers')[0]
            url_imagen=f'https://covers.openlibrary.org/b/id/{id_imagen}-L.jpg' #
        except:
            id_imagen=''
            url_imagen=''

    else:
        nombre=''
        fec_publicacion=''
        editorial=''
        descripcion=''
        formato=''
        paginas=''
        url_imagen=''

    datos={
        "nombre": nombre,
        "fec_publicacion": fec_publicacion,
        "editorial":editorial,
        "descripcion": descripcion,
        "formato": formato,
        "paginas": paginas,
        "url_imagen": url_imagen
    }
    return datos

#print(obtener_datos(9788420664446))