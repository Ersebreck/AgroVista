import folium
from streamlit_folium import st_folium
import streamlit as st
from shapely.geometry import shape
from utils import obtener_terrenos, obtener_ubicacion, obtener_parcelas_por_terreno, obtener_parcela

def mostrar_mapa_general():
    st.subheader("🗺️ Mapa de Terrenos")

    terrenos = obtener_terrenos()
    if not terrenos:
        st.warning("No hay terrenos registrados.")
        return

    mapa = folium.Map(location=[4.6, -74.1], zoom_start=6)

    for terreno in terrenos:
        ubicacion_id = terreno.get("ubicacion_id")
        if not ubicacion_id:
            continue

        ubic = obtener_ubicacion(ubicacion_id)
        coords = ubic.get("coordenadas", {})
        if ubic.get("tipo") == "poligono" and coords.get("type") == "Polygon":
            folium.GeoJson(
                coords,
                name=terreno["nombre"],
                tooltip=terreno["nombre"],
                style_function=lambda x: {"color": "green", "fillOpacity": 0.4}
            ).add_to(mapa)

    st_folium(mapa, width=900, height=600)

def mostrar_mapa_parcelas_por_terreno():
    st.subheader("📍 Parcelas por Terreno")

    terrenos = obtener_terrenos()
    if not terrenos:
        st.warning("No hay terrenos.")
        return

    opciones = {f"{t['nombre']} (ID {t['id']})": t['id'] for t in terrenos}
    seleccion = st.selectbox("Selecciona un terreno", list(opciones.keys()))
    terreno_id = opciones[seleccion]

    parcelas = obtener_parcelas_por_terreno(terreno_id)
    if not parcelas:
        st.info("Este terreno no tiene parcelas.")
        return

    mapa = folium.Map(location=[4.6, -74.1], zoom_start=7)

    for parcela in parcelas:
        ubicacion_id = parcela.get("ubicacion_id")
        if not ubicacion_id:
            continue

        ubic = obtener_ubicacion(ubicacion_id)
        coords = ubic.get("coordenadas", {})
        estado = parcela.get("estado", "desconocido")

        color = "blue" if estado == "activa" else "gray"

        if ubic.get("tipo") == "poligono" and coords.get("type") == "Polygon":
            folium.GeoJson(
                coords,
                name=parcela["nombre"],
                tooltip=f"{parcela['nombre']} - {estado}",
                style_function=lambda x, col=color: {"color": col, "fillOpacity": 0.5}
            ).add_to(mapa)

    st_folium(mapa, width=900, height=600)
