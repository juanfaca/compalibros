import streamlit as st
from pruebas import precios
from openlibrary import obtener_datos

def main():
    # Título y bienvenida
    st.title("Compalibros")
    st.header("Encuentra el mejor precio para tu libro")
    st.text("Ingresa el ISBN del libro que deseas buscar:")

    # Ingreso del ISBN por parte del usuario
    isbn = st.text_input("Ingresa el ISBN del libro")
    isbn = str(isbn).replace('-','')
    st.write(isbn)

    # Ejecución de la búsqueda
    if st.button("Buscar"):
        # Webscraping de precios
        data=precios(isbn)
        # Webscraping de información general del libro
        json_libro=obtener_datos(isbn)
        nombre=json_libro.get('nombre') #Nombre del libro
        fec_publicacion=json_libro.get('fec_publicacion') #Fecha de publicación del libro
        descripcion=json_libro.get('descripcion') #Descripción del libro
        formato=json_libro.get('formato') #Formato del libro: tapa blanda, tapa dura, etc
        paginas=json_libro.get('paginas') #Nro de páginas del libro
        url_imagen=json_libro.get('url_imagen') #Url con recurso de la imagen del libro

# Esto asegura que la función main() se ejecute cuando el script es corrido por Streamlit
if __name__ == "__main__":
    main()