import requests
from folium import GeoJson, GeoJsonTooltip
import streamlit as st
from datetime import date, timedelta
import pandas as pd
from collections import Counter

API_URL = "http://localhost:8000"  # Ajusta si corres desde Docker o con dominio

def resumen_estado_parcelas(estado_parcelas):
    resumen = Counter({
        "Óptimo": 0,
        "Atención": 0,
        "Crítico": 0
    })

    for estados in estado_parcelas.values():
        if "Inactiva" in estados:
            resumen["Crítico"] += 1
        elif "Pendiente de intervención" in estados:
            resumen["Atención"] += 1
        elif "Activa" in estados:
            resumen["Óptimo"] += 1
        else:
            # Por si no encaja en ninguno, cuenta como 'Atención'
            resumen["Atención"] += 1

    return resumen


def evaluar_estado_parcelas(df_actividades):
    hoy = pd.Timestamp.today().normalize()  # <-- Cambio aquí
    estado_parcelas = {}

    actividades_por_parcela = df_actividades.groupby("parcela_id")

    for parcela_id, grupo in actividades_por_parcela:
        grupo = grupo.copy()
        grupo["fecha"] = pd.to_datetime(grupo["fecha"], errors="coerce")

        fechas = grupo["fecha"]
        tipos = grupo["tipo"].tolist()
        ultima_fecha = fechas.max()
        dias_sin_actividad = (hoy - ultima_fecha).days

        estado = []

        if dias_sin_actividad <= 5:
            estado.append("Activa")
        elif dias_sin_actividad <= 10:
            estado.append("Pendiente de intervención")
        else:
            estado.append("Inactiva")

        if "Cosecha" in tipos:
            fechas_cosecha = grupo[grupo["tipo"] == "Cosecha"]["fecha"]
            fechas_cosecha = pd.to_datetime(fechas_cosecha, errors="coerce")
            if any((hoy - fechas_cosecha).dt.days <= 3):
                estado.append("Cosechada recientemente")

        tareas_recientes = grupo[grupo["fecha"] >= hoy - timedelta(days=3)]
        if len(tareas_recientes) >= 3:
            estado.append("Alta carga de tareas")

        if grupo["tipo"].isin(["Cosecha", "Ordeño", "Pesaje"]).any():
            estado.append("Tiene productividad")

        estado_parcelas[parcela_id] = estado

    return estado_parcelas

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
