import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from ibero import obtener_datos as ibero
from communitas import obtener_datos as communitas
from crisol import obtener_datos as crisol
from elvirrey import obtener_datos as elvirrey

def precios(x):
    columnas = ['url_producto', 'precio_venta', 'disponibilidad']

    funciones = {
        'Ibero Librerías': ibero,
        'Librería Communitas': communitas,
        'Crisol': crisol,
        'Librería El Virrey': elvirrey
    }

    resultados = pd.DataFrame()

    for nombre, funcion in funciones.items():
        try:
            resultado = funcion(x)[columnas]
            if not resultado.empty:
                resultado.insert(0, "Librería", nombre)
                resultados = pd.concat([resultados, resultado], ignore_index=True)
        except Exception:
            continue

    if not resultados.empty:
        resultados['precio_venta'] = pd.to_numeric(resultados['precio_venta'], errors='coerce').round(1)
        resultados = resultados.sort_values(by='precio_venta', ascending=True)

    return resultados

#isbn=9788483933558
#print(precios(isbn))