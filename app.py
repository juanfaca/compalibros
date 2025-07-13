import streamlit as st
from pruebas import precios
from openlibrary import obtener_datos
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- Configuración de la página ---
st.set_page_config(
    page_title="Compalibros: Encuentra el Mejor Precio para tu Libro",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Monitoreo con G4A ---
ga4_measurement_id = st.secrets.get("google_analytics_id", None)

if ga4_measurement_id:
    google_analytics_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga4_measurement_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', '{ga4_measurement_id}');
    </script>
    """
    st.markdown(google_analytics_code, unsafe_allow_html=True)
else:
    print("ID de Google Analytics no encontrado en Streamlit Secrets. El seguimiento no estará activo")

# --- Inicialización de Firebase (solo una vez al inicio de la aplicación) ---
# Este bloque se asegura de que Firebase se inicialice solo una vez por sesión de Streamlit.
if not firebase_admin._apps:
    try:
        # Intenta cargar las credenciales desde st.secrets (para despliegues en Streamlit Cloud)
        if "gcp_service_account" in st.secrets:
            # Convierte el diccionario de secretos a un diccionario de credenciales de Firebase.
            # La clave privada puede necesitar un reemplazo de \n si no se maneja automáticamente
            creds_dict = st.secrets["gcp_service_account"]
            # Asegúrate de que la private_key tenga los saltos de línea correctos
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')

            cred = credentials.Certificate(creds_dict)
            # Mensaje de éxito ahora se imprime en la consola, no en la UI
            print("Conexión a Firestore establecida usando Streamlit Secrets.")
        else:
            # Mensaje de advertencia ahora se imprime en la consola, no en la UI
            print("ADVERTENCIA: No se encontró 'gcp_service_account' en st.secrets. Intentando cargar credenciales por defecto (solo para desarrollo local).")
            cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(cred)
        db = firestore.client() # Obtiene la instancia del cliente de Firestore
    except Exception as e:
        print(f"Error al inicializar Firebase: {e}")
        print("Asegúrate de que tus credenciales de Firebase estén configuradas correctamente en Streamlit Secrets o localmente.")
        st.stop()

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

        # --- PREPARAR Y GUARDAR DATOS EN FIRESTORE ---
        # Inicializa los precios para las librerías específicas con None
        firestore_prices = {
            'precio_communitas': None,
            'precio_el_virrey': None,
            'precio_ibero': None,
            'precio_crisol': None
        }

        # Mapea los nombres de las librerías del DataFrame a los campos de Firestore
        bookstore_map = {
            'communitas': 'precio_communitas',
            'el virrey': 'precio_el_virrey',
            'ibero': 'precio_ibero',
            'crisol': 'precio_crisol'
        }

        # Itera sobre los datos para extraer los precios y mapearlos
        for _, row in data.iterrows():
            libreria_name = row.get('librería', '').lower().strip()
            price_value = row.get('precio')

            # Verifica si el precio es válido y conviértelo a float si no es None/NaN
            if pd.notnull(price_value) and price_value != '' and price_value is not None:
                try:
                    price_value = float(price_value)
                except ValueError:
                    price_value = None # Deja como None si la conversión falla
            else:
                price_value = None # Establece a None si no está disponible

            if libreria_name in bookstore_map:
                firestore_prices[bookstore_map[libreria_name]] = price_value

        # Crea el documento a guardar en Firestore
        search_data = {
            'isbn': isbn,
            'fecha_consulta': datetime.now(), # Timestamp actual con fecha y hora
            'nombre_libro': nombre,
            **firestore_prices # Desempaqueta el diccionario de precios en el documento
        }

        # Guarda el documento en Firestore
        try:
            # Asegúrate de que 'db' esté inicializado y disponible antes de intentar guardar
            if 'db' in locals() or 'db' in globals():
                # Usa la colección 'busquedas_libros' que creaste en Firestore
                doc_ref = db.collection('busquedas_libros').add(search_data)
                st.success(f"Datos de la búsqueda guardados en Firestore con ID: {doc_ref[1].id}")
            else:
                st.error("Error: La conexión a Firestore no se estableció correctamente. No se pudieron guardar los datos.")
        except Exception as e:
            st.error(f"Error al guardar los datos en Firestore: {e}")
        # --- FIN DE LA SECCIÓN DE FIRESTORE ---

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