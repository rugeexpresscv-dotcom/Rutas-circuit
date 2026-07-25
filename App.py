import streamlit as st
from google import genai
import pandas as pd
from PIL import Image
import io
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador CSV Circuit", page_icon="📦")
st.title("📦 Extraer Direcciones para Circuit")
st.write("Sube las capturas de tu ruta y obtén el archivo CSV listo para importar.")

api_key = st.text_input("Ingresa tu API Key de Google Gemini", type="password")

uploaded_files = st.file_uploader("Sube las capturas (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if api_key and uploaded_files:
    if st.button("Generar CSV"):
        with st.spinner("Procesando imágenes..."):
            try:
                # Inicializar el cliente con la nueva SDK unificada
                client = genai.Client(api_key=api_key)
                
                prompt = """
                Extrae las direcciones y el número de paquete de las imágenes de la ruta.
                Devuelve los datos ESTRICTAMENTE en este formato CSV:
                
                Address,City,Note
                [Direccion], La Florida, Santiago, Chile, [Numero de paquete]
                """
                
                # Preparar los contenidos compatibles con la nueva API
                contents = [prompt]
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.getvalue()
                    contents.append(
                        genai.types.Part.from_bytes(
                            data=bytes_data,
                            mime_type=uploaded_file.type
                        )
                    )
                
                # Llamada al modelo vigente usando gemini-2.0-flash
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=contents,
                )
                
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
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")
