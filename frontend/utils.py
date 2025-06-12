import requests
from folium import GeoJson, GeoJsonTooltip
import streamlit as st
API_URL = "http://localhost:8000"  # Ajusta si corres desde Docker o con dominio

def chatbot_response():
    # Mostrar todo el historial
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Chatea con AgroVista"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Respuesta simulada del sistema
        respuesta = f"Simulación de respuesta para: {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()
    if st.button("🧹 Limpiar chat"):
        st.session_state["messages"] = [{"role": "assistant", "content": hola}]
        st.rerun()


def add_geojson_polygon(grupo, name, coords, color, opacity):
    feature = {
        "type": "Feature",
        "properties": {"name": name},
        "geometry": {"type": "Polygon", "coordinates": [[ [lon, lat] for lat, lon in coords ]]}
    }
    GeoJson(
        feature,
        tooltip=GeoJsonTooltip(fields=["name"], aliases=["Nombre:"], sticky=True),
        style_function=lambda x: {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": opacity,
        }
    ).add_to(grupo)

def obtener_terrenos():
    try:
        res = requests.get(f"{API_URL}/terrenos")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener terrenos: {e}")
        return []

def obtener_parcelas_por_terreno(terreno_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/por-terreno/{terreno_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcelas: {e}")
        return []

def obtener_parcela(parcela_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/{parcela_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcela: {e}")
        return {}

def obtener_ubicacion(ubicacion_id):
    try:
        res = requests.get(f"{API_URL}/ubicaciones/{ubicacion_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener ubicación: {e}")
        return {}

def registrar_actividad(data):
    try:
        res = requests.post(f"{API_URL}/actividades/", json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al registrar actividad: {e}")
        return None
