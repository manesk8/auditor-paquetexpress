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

st.title("🛡️ Auditor Inteligente - By Emma")
st.write("Introduce las medidas manuales de la guía y los datos reales del dimensionador para auditar el volumen.")

# Variables donde guardaremos lo que descubra la IA en la foto
largo_guia = 0.0
ancho_guia = 0.0
alto_guia = 0.0
st.info("Escribe las medidas de la guía manualmente de forma rápida:")
largo_guia = st.number_input("Largo de Guía Manual (cm)", min_value=0.0, value=100.0)
ancho_guia = st.number_input("Ancho de Guía Manual (cm)", min_value=0.0, value=120.0)
alto_guia = st.number_input("Alto de Guía Manual (cm)", min_value=0.0, value=80.0)
# 2. Datos del Dimensionador Mettler Toledo (Lo real en el almacén)
st.subheader("📊 Datos del Dimensionador")
largo_real = st.number_input("Largo Real del Dimensionador (cm)", min_value=0.0, value=100.0)
ancho_real = st.number_input("Ancho Real del Dimensionador (cm)", min_value=0.0, value=120.0)
alto_real = st.number_input("Alto Real del Dimensionador (cm)", min_value=0.0, value=80.0)

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
        
