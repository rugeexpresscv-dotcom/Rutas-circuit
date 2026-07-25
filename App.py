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

api_key = st.text_input("Ingresa tu API Key de Google Gemini:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    uploaded_files = st.file_uploader("Sube las capturas (JPG/PNG)", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
    if uploaded_files and st.button("Generar CSV"):
        with st.spinner("Procesando imágenes..."):
            prompt = """
            Extrae las direcciones y el número de paquete de las imágenes adjuntas. 
            Devuelve los datos ESTRICTAMENTE en este formato CSV:
            
            Address,City,Note
            [Direccion], La Florida, Santiago, Chile,Santiago,[Numero de paquete]
            
            Reglas:
            1. Solo devuelve las líneas de datos, nada de texto extra.
            2. Reemplaza '[Direccion]' por la calle y número.
            3. Reemplaza '[Numero de paquete]' por el número de bulto.
            4. No uses bloques de código.
            """
            
            images = [Image.open(file) for file in uploaded_files]
            
            try:
                response = model.generate_content([prompt] + images)
                csv_data = response.text.strip()
                
                if csv_data.startswith("```csv"):
                    csv_data = csv_data.replace("```csv", "").replace("```", "").strip()
                elif csv_data.startswith("```"):
                    csv_data = csv_data.replace("```", "").strip()
                
                # Procesar datos y limpiar duplicados / agrupar bultos
                df = pd.read_csv(io.StringIO(csv_data))
                df['Note'] = df['Note'].astype(str)
                df = df.drop_duplicates(subset=['Address', 'City', 'Note'])
                df = df.groupby(['Address', 'City'], as_index=False).agg({
                    'Note': lambda x: ' y '.join(x.unique())
                })
                
                st.success("¡Datos extraídos con éxito!")
                st.dataframe(df)
                
                # --- FECHA DINÁMICA PARA EL ARCHIVO ---
                fecha_hoy = datetime.now().strftime('%Y-%m-%d')
                nombre_archivo = f'ruta_circuit_{fecha_hoy}.csv'
                # --------------------------------------
                
                csv_bytes = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV para Circuit",
                    data=csv_bytes,
                    file_name=nombre_archivo,
                    mime='text/csv',
                )
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
else:
    st.info("Ingresa tu API Key para continuar.")
