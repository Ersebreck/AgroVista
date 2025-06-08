import streamlit as st
from components import mapa, fichas, registro

st.set_page_config(page_title="AgroVista", layout="wide")
st.title("AgroVista 🌱")

st.sidebar.header("📋 Menú Principal")
opcion = st.sidebar.selectbox("¿Qué deseas hacer?", [
    "🗺️ Ver Mapa de Terrenos",
    "📍 Ver Parcelas por Terreno",
    "🔍 Detalle de Parcela",
    "🛠️ Registrar Actividad"
])

# Enrutamiento de opciones
if opcion == "🗺️ Ver Mapa de Terrenos":
    mapa.mostrar_mapa_general()

elif opcion == "📍 Ver Parcelas por Terreno":
    mapa.mostrar_mapa_parcelas_por_terreno()

elif opcion == "🔍 Detalle de Parcela":
    fichas.ver_detalle_parcela()

elif opcion == "🛠️ Registrar Actividad":
    registro.formulario_registro()
