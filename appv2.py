import streamlit as st
from pruebas import precios
from openlibrary import obtener_datos
import pandas as pd

# Estilo personalizado (opcional)
st.set_page_config(page_title="Compalibros", page_icon="📚", layout="centered")

def main():
    # Encabezado de la app
    st.markdown("<h1 style='text-align: center; color: #336699;'>📚 Compalibros</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Encuentra el mejor precio para tu libro</h3>", unsafe_allow_html=True)
    st.markdown("")

    # Input para el ISBN
    isbn = st.text_input("🔎 Ingresa el ISBN del libro que deseas buscar")
    isbn = str(isbn).replace('-', '').strip()

    if st.button("Buscar"):
        with st.spinner("Buscando información..."):
            # Obtener precios
            data = precios(isbn)

            # Obtener datos del libro
            json_libro = obtener_datos(isbn)
            nombre = json_libro.get('nombre', 'No disponible')
            fec_publicacion = json_libro.get('fec_publicacion', 'No disponible')
            descripcion = json_libro.get('descripcion', 'No disponible')
            formato = json_libro.get('formato', 'No disponible')
            paginas = json_libro.get('paginas', 'No disponible')
            url_imagen = json_libro.get('url_imagen', None)

        # Mostrar resultados
        st.markdown("---")
        col1, col2 = st.columns([1, 2])

        with col1:
            if url_imagen:
                st.image(url_imagen, caption=nombre, use_container_width=True)
            else:
                st.warning("No se encontró imagen para este libro.")

        with col2:
            st.markdown(f"### 📖 {nombre}")
            st.markdown(f"**🗓 Fecha de publicación:** {fec_publicacion}")
            st.markdown(f"**📘 Formato:** {formato}")
            st.markdown(f"**📄 Número de páginas:** {paginas}")
            st.markdown(f"**📝 Descripción:**\n{descripcion}")

        st.markdown("---")
        st.subheader("💰 Comparación de precios")

        if isinstance(data, pd.DataFrame) and not data.empty:
            # Ordenar precios de menor a mayor si existe columna 'precio'
            if 'precio' in data.columns:
                data = data.sort_values('precio')
            st.dataframe(data, use_container_width=True)
        else:
            st.error("No se encontraron precios para este ISBN.")

# Ejecutar la app
if __name__ == "__main__":
    main()