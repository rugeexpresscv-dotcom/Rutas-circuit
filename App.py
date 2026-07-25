import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador CSV Circuit", page_icon="📦")
st.title("📦 Extraer Direcciones para Circuit")
st.write("Sube las capturas de tu ruta y obtén el archivo CSV listo para importar.")

api_key = st.text_input("Ingresa tu API Key de Google Gemini", type="password")

if api_key:
    genai.configure(api_key=api_key)

# Definimos el modelo fuera de condiciones para asegurar disponibilidad global
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("Sube las capturas (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files and st.button("Generar CSV"):
    with st.spinner("Procesando imágenes..."):
        prompt = """
        Extrae las direcciones y el número de paquete de las imágenes de la ruta.
        Devuelve los datos ESTRICTAMENTE en este formato CSV:
        
        Address,City,Note
        [Direccion], La Florida, Santiago, Chile, [Numero de paquete]
        """
        
        image_parts = []
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()
            image_parts.append({"mime_type": uploaded_file.type, "data": bytes_data})
        
        response = model.generate_content([prompt, *image_parts])
        
        # Generar nombre del archivo con fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"ruta_circuit_{fecha_actual}.csv"
        
        st.subheader("Resultado:")
        st.code(response.text, language="csv")
        
        st.download_button(
            label="Descargar CSV para Circuit",
            data=response.text,
            file_name=nombre_archivo,
            mime="text/csv"
        )
