import streamlit as st
from pruebas import precios
from openlibrary import obtener_datos
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(
    page_title="Compalibros: Encuentra el Mejor Precio para tu Libro",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Estilos CSS personalizados ---
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .subheader {
        font-size: 1.5em;
        color: #555;
        text-align: center;
        margin-bottom: 2em;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 1.2em;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 5px 5px 10px rgba(0,0,0,0.3);
    }
    .book-info-card {
        background-color: #f9f9f9;
        border-left: 5px solid #4CAF50;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .book-title {
        font-size: 1.8em;
        color: #333;
        margin-bottom: 0.5em;
    }
    .book-detail {
        font-size: 1.1em;
        color: #666;
        margin-bottom: 0.3em;
    }
    .bookstore-card {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #c8e6c9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .bookstore-name {
        font-size: 1.3em;
        color: #2e7d32;
        font-weight: bold;
    }
    .bookstore-price {
        font-size: 1.2em;
        color: #d32f2f;
        font-weight: bold;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Cabecera de la Aplicación ---
st.markdown("<h1 class='main-header'>Compalibros</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Encuentra el mejor precio para tu libro</p>", unsafe_allow_html=True)

# --- Sección de Entrada de ISBN ---
st.info("📚 Ingresa el **ISBN** (International Standard Book Number) del libro que deseas buscar.")
isbn = st.text_input("Ingresa el ISBN del libro (Ej: 978-0321765723)", help="Puedes encontrar el ISBN en la contraportada del libro o en su página de detalles online.")
isbn = str(isbn).replace('-', '').strip()

# --- Sidebar ---
st.sidebar.title("Acerca de Compalibros")
st.sidebar.info(
    "Esta aplicación te ayuda a comparar precios de libros en diferentes librerías utilizando el ISBN del libro. "
    "¡Esperamos que te sea útil para encontrar las mejores ofertas!"
)

st.sidebar.markdown("---")

st.sidebar.markdown("**Desarrollado por** [Juan Collantes](https://www.linkedin.com/in/juancollantesan/)")

st.sidebar.markdown(
    """
    📬 **Para trabajos similares** (Web scraping, Análisis de datos o similares):  
    [juanfieecs@gmail.com](mailto:juanfieecs@gmail.com)
    """
)

# --- Búsqueda ---
if st.button("Buscar"):
    with st.spinner("Buscando información..."):
        # Obtener precios y datos del libro
        data = precios(isbn)
        json_libro = obtener_datos(isbn)

    nombre = json_libro.get('nombre')
    editorial = json_libro.get('editorial')
    fec_publicacion = json_libro.get('fec_publicacion')
    descripcion = json_libro.get('descripcion')
    formato = json_libro.get('formato')
    paginas = json_libro.get('paginas')
    url_imagen = json_libro.get('url_imagen')

    # --- Información del libro ---
    col1, col2 = st.columns([1, 2])
    with col1:
        if url_imagen:
            st.image(url_imagen, caption=nombre, use_container_width=True)
        else:
            st.warning("No se encontró imagen del libro.")
    with col2:
        html_info = f"""
        <div class='book-info-card'>
            <div class='book-title'>{nombre}</div>
            <div class='book-detail'><b>📘 Editorial:</b> {editorial}</div>
            <div class='book-detail'><b>📅 Fecha de publicación:</b> {fec_publicacion}</div>
            <div class='book-detail'><b>📘 Formato:</b> {formato}</div>
            <div class='book-detail'><b>📄 Número de páginas:</b> {paginas}</div>
            <div class='book-detail'><b>📝 Descripción:</b><br>{descripcion}</div>
        </div>
        """
        st.markdown(html_info, unsafe_allow_html=True)

    # --- Comparación de precios ---
    st.subheader("💰 Comparación de precios en librerías")
    if isinstance(data, pd.DataFrame) and not data.empty:
        # Normaliza columnas
        data.columns = [col.lower().strip() for col in data.columns]
        data = data.rename(columns={
            'libreria': 'librería',
            'precio_venta': 'precio',
            'url_producto': 'url',
            'disponibilidad': 'stock'
        })

        # Ordena por precio si se puede
        try:
            data['precio'] = data['precio'].astype(float)
            data = data.sort_values(by='precio')
        except:
            pass

        for _, row in data.iterrows():
            libreria = row.get('librería', 'Librería')
            precio = row.get('precio', '--')
            if pd.isnull(precio) or precio == '' or precio is None:
                precio = "No Disponible"
            stock = row.get('stock', 'Sin info')
            url = row.get('url', None)
            html = f"""
            <div class='bookstore-card'>
                <div class='bookstore-name'>{libreria}</div>
                <div class='bookstore-price'>📗 Precio: {"S/ " + str(precio) if precio != "No Disponible" else precio}</div>
                <div class='book-detail'>📦 Disponibilidad: {stock}</div>
            """

            if isinstance(url, str) and url.startswith("http"):
                html += f"<a href='{url}' target='_blank'>🛒 Ir a la librería</a>"

            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)