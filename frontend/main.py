import streamlit as st
from modules.simulaciones import mostrar_simulaciones
from modules.reportes import vista_reportes

st.set_page_config(page_title="AgroVista", layout="wide")

st.sidebar.title("🌱 AgroVista")
pagina = st.sidebar.radio("Navegación", ["Mapa Interactivo", "Simulaciones", "Reportes"])

if pagina == "Mapa Interactivo":
    from map import vista_mapa
    vista_mapa()

elif pagina == "Simulaciones":
    
    mostrar_simulaciones()

elif pagina == "Reportes":
    vista_reportes()
