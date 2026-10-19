import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re

# 1. Configuración inicial y carga del lector de IA (Se guarda en memoria para ir rápido)
@st.cache_resource
def cargar_lector_ia():
    # Carga el lector en español e inglés
    return easyocr.Reader(['es', 'en'], gpu=False)

reader = cargar_lector_ia()

st.title("🛡️ Auditor Inteligente - Paquetexpress")
st.write("Toma foto a la guía y el sistema calculará las diferencias de volumen automáticamente.")

# 2. Datos del Dimensionador Mettler Toledo (Lo real en el almacén)
st.subheader("📊 Datos del Dimensionador")
largo_real = st.number_input("Largo Real del Dimensionador (cm)", min_value=0.0, value=160.0)
ancho_real = st.number_input("Ancho Real del Dimensionador (cm)", min_value=0.0, value=130.0)
alto_real = st.number_input("Alto Real del Dimensionador (cm)", min_value=0.0, value=95.0)

# 3. El botón de la cámara con EasyOCR
st.subheader("📸 Captura de Guía Física")
foto_guia = st.camera_input("Toma una foto muy clara y derecha de la zona de medidas de la guía")

# Variables donde guardaremos lo que descubra la IA en la foto
largo_guia = 0.0
ancho_guia = 0.0
alto_guia = 0.0

if foto_guia is not None:
    # Procesar la imagen para que la IA la entienda
    imagen = Image.open(foto_guia)
    imagen_np = np.array(imagen)
    
    with st.spinner("🧠 La IA está leyendo la guía... espera un momento."):
        # EasyOCR lee todo el texto de la foto y lo mete en una lista
        textos_detectados = reader.readtext(imagen_np, detail=0)
        
    st.success("¡Lectura terminada!")
    
    # Unimos todo el texto en una sola frase larga para buscar adentro
    texto_completo = " ".join(textos_detectados).lower()
    
    # Muestra en tu pantalla todo lo que leyó la IA (Sirve mucho para revisar qué detecta)
    with st.expander("🔍 Ver texto detectado por el escáner"):
        st.write(textos_detectados)

    # 4. Inteligencia de búsqueda (Buscamos el patrón clásico de medidas: ej. 150x120x80)
    # Esta línea busca combinaciones de "números x números x números"
    patron_medidas = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', texto_completo)
    
    if patron_medidas:
        largo_guia = float(patron_medidas.group(1))
        ancho_guia = float(patron_medidas.group(2))
        alto_guia = float(patron_medidas.group(3))
        
        st.metric(label="📐 Medidas extraídas de la Guía:", value=f"{int(largo_guia)} x {int(ancho_guia)} x {int(alto_guia)} cm")
    else:
        st.warning("⚠️ No logré detectar el formato 'NÚMERO x NÚMERO x NÚMERO' en la foto. Por favor, asegúrate de que la foto tenga buena luz y esté derecha.")
        
        # Casillas de respaldo por si la foto sale borrosa o falla el OCR
        st.info("Escribe las medidas de la guía manualmente de forma rápida:")
        largo_guia = st.number_input("Largo de Guía Manual (cm)", min_value=0.0, value=150.0)
        ancho_guia = st.number_input("Ancho de Guía Manual (cm)", min_value=0.0, value=120.0)
        alto_guia = st.number_input("Alto de Guía Manual (cm)", min_value=0.0, value=80.0)

    # 5. Botón final para ejecutar la auditoría matemática
    if st.button("🚨 Verificar Tarima"):
        vol_guia = (largo_guia * ancho_guia * alto_guia) / 1000000
        vol_real = (largo_real * ancho_real * alto_real) / 1000000
        diferencia_vol = vol_real - vol_guia
        
        st.write(f"*Volumen Calculado de la Guía:* {vol_guia:.3f} m³")
        st.write(f"*Volumen Real del Dimensionador:* {vol_real:.3f} m³")
        st.write(f"*Diferencia de Volumen:* {diferencia_vol:.3f} m³")
        
        # Lógica de decisión con tu criterio de negocio (.10 m³)
        if diferencia_vol >= 0.10:
            st.error(f"🔴 *¡ALERTA ROJA!* Diferencia crítica de {diferencia_vol:.3f} m³. ¡SÚBELA AL WHATSAPP!")
        elif diferencia_vol > 0 and diferencia_vol < 0.10:
            st.warning(f"⚠️ Diferencia leve de {diferencia_vol:.3f} m³. No es necesario reportar al grupo.")
        else:
            st.success("✅ Todo en orden. El volumen real es menor o igual al documentado.")
        