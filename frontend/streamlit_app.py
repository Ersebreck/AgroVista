import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import GeoJson, GeoJsonTooltip
import pandas as pd
from datetime import date, timedelta
import random

# ----------------------------
# 1. Datos simulados en memoria

# Simulated data for the minimal database

# Terrenos
terrenos = pd.DataFrame([
    {"id": 1, "nombre": "Terreno 1", "descripcion": "Cultivo de maíz"},
    {"id": 2, "nombre": "Terreno 2", "descripcion": "Ganadería"}
])

# Parcelas
parcelas = pd.DataFrame([
    {"id": 1, "nombre": "Parcela 1A", "terreno_id": 1, "uso_actual": "Maíz joven", "estado": "activo"},
    {"id": 2, "nombre": "Parcela 1B", "terreno_id": 1, "uso_actual": "Maíz maduro", "estado": "cosecha"},
    {"id": 3, "nombre": "Parcela 2A", "terreno_id": 2, "uso_actual": "Pasto", "estado": "activo"},
    {"id": 4, "nombre": "Parcela 2B", "terreno_id": 2, "uso_actual": "Corrales", "estado": "mantenimiento"}
])

# Simulate activity logs (10 per parcela)
tipos_actividad = ["Riego", "Fertilización", "Fumigación", "Cosecha", "Siembra", "Limpieza"]
actividades = []

for parcela_id in parcelas["id"]:
    base_date = date(2025, 6, 1)
    for i in range(10):
        actividad = {
            "id": len(actividades) + 1,
            "parcela_id": parcela_id,
            "tipo": random.choice(tipos_actividad),
            "descripcion": "Tarea realizada",
            "fecha": base_date + timedelta(days=random.randint(0, 15))
        }
        actividades.append(actividad)

actividades_df = pd.DataFrame(actividades)


# ----------------------------

# Información de parcelas
parcelas_info = {
    'Terreno 1': "🌽 Cultivo de maíz.\nUso mixto: joven y maduro.",
    'Parcela 1A': "🌱 Maíz joven.\nÁrea experimental.",
    'Parcela 1B': "🌽 Maíz maduro.\nListo para cosecha.",
    'Terreno 2': "🐄 Ganadería.\nDivisión entre pasto y corrales.",
    'Parcela 2A': "🌾 Zona de pasto.\nRotación semanal.",
    'Parcela 2B': "🐖 Corrales.\nRequiere limpieza.",
}

# ID por nombre para lookup rápido
parcelas_ids = {
    'Parcela 1A': 1, 'Parcela 1B': 2, 'Parcela 2A': 3, 'Parcela 2B': 4
}

# Generar actividades simuladas
tipos_actividad = ["Riego", "Fertilización", "Fumigación", "Cosecha", "Siembra", "Limpieza"]
actividades = []
base_date = date(2025, 6, 1)

for nombre, pid in parcelas_ids.items():
    for _ in range(10):
        actividades.append({
            "parcela_id": pid,
            "nombre": nombre,
            "tipo": random.choice(tipos_actividad),
            "descripcion": "Tarea realizada",
            "fecha": base_date + timedelta(days=random.randint(0, 15))
        })
df_actividades = pd.DataFrame(actividades)

# ----------------------------
# 2. Interfaz de Streamlit
# ----------------------------

st.set_page_config(layout="wide")
st.title("🌱 AgroVista")
st.sidebar.title("📘 Información")

# Crear mapa base
m = folium.Map(location=[4.7110, -74.0721], zoom_start=13)

# Agregar polígonos
def add_geojson_polygon(name, coords, color):
    feature = {
        "type": "Feature",
        "properties": {"name": name},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[ [lon, lat] for lat, lon in coords ]]
        }
    }
    GeoJson(
        feature,
        tooltip=GeoJsonTooltip(
            fields=["name"],
            aliases=["Nombre:"],
            sticky=True,
            style="background-color: white; border: 1px solid black; border-radius: 3px; padding: 5px;",
        ),
        style_function=lambda x: {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.5,
        }
    ).add_to(m)

# Definir polígonos
add_geojson_polygon("Terreno 1", [
    [4.715, -74.08], [4.715, -74.075], [4.712, -74.075], [4.712, -74.08]
], "green")
add_geojson_polygon("Parcela 1A", [
    [4.7145, -74.079], [4.7145, -74.078], [4.7135, -74.078], [4.7135, -74.079]
], "lightgreen")
add_geojson_polygon("Parcela 1B", [
    [4.7132, -74.077], [4.7132, -74.076], [4.7125, -74.076], [4.7125, -74.077]
], "lightgreen")
add_geojson_polygon("Terreno 2", [
    [4.709, -74.07], [4.709, -74.065], [4.706, -74.065], [4.706, -74.07]
], "blue")
add_geojson_polygon("Parcela 2A", [
    [4.7085, -74.069], [4.7085, -74.068], [4.7078, -74.068], [4.7078, -74.069]
], "lightblue")
add_geojson_polygon("Parcela 2B", [
    [4.7072, -74.067], [4.7072, -74.066], [4.7065, -74.066], [4.7065, -74.067]
], "lightblue")

# ----------------------------
# 2 columnas: Mapa + Gráfica
# ----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### Mapa interactivo")
    output = st_folium(m, width=700, height=500, return_on_hover=False)

with col2:
    clicked = output["last_object_clicked_tooltip"]

    if clicked:
        clicked = clicked.split("\n")[-2].replace("  ","")
        st.markdown(f"### 📊 Visualización – {clicked}")

        opciones = ["Frecuencia de actividades", "Última actividad", "Tipo dominante"]
        vista = st.selectbox("Selecciona vista:", opciones)

        if clicked in parcelas_ids:
            df_parcela = df_actividades[df_actividades["nombre"] == clicked]

            if vista == "Frecuencia de actividades":
                freq = df_parcela["tipo"].value_counts()
                st.bar_chart(freq)

            elif vista == "Última actividad":
                ultima = df_parcela.sort_values("fecha", ascending=False).iloc[0]
                st.markdown(f"**{ultima['tipo']}** – {ultima['fecha'].strftime('%d %b')}")

            elif vista == "Tipo dominante":
                tipo = df_parcela["tipo"].mode()[0]
                st.markdown(f"🔁 Actividad más común: **{tipo}**")
        else:
            st.markdown("Selecciona una parcela.")
    else:
        st.markdown("Haz clic en una parcela o terreno para ver la visualización.")


# ----------------------------
# 3. Mostrar info seleccionada
# ----------------------------

clicked = output["last_object_clicked_tooltip"]

if clicked:
    clicked = clicked.split("\n")[-2].replace("  ","")
    st.sidebar.markdown(f"### 🏡 {clicked}")
    st.sidebar.markdown(parcelas_info.get(clicked, "Sin información."))

    if clicked in parcelas_ids:
        df_parcela = df_actividades[df_actividades["nombre"] == clicked]
        df_parcela = df_parcela.sort_values("fecha", ascending=False).head(5)

        st.sidebar.markdown("#### Últimas actividades")
        for _, row in df_parcela.iterrows():
            st.sidebar.markdown(f"- **{row['tipo']}** – {row['fecha'].strftime('%d %b')}")


    elif clicked in terrenos["nombre"].values:
        terreno_id = terrenos[terrenos["nombre"] == clicked]["id"].values[0]
        # Mostrar cuántas parcelas contiene ese terreno
        n = parcelas[parcelas["terreno_id"] == terreno_id].shape[0]
        st.sidebar.info(f"Este terreno tiene **{n} parcelas**.")
        # Mostrar las parcelas asociadas
        parcelas_terreno = parcelas[parcelas["terreno_id"] == terreno_id]
        st.sidebar.markdown(f"#### Parcelas en {clicked}:")
        for _, row in parcelas_terreno.iterrows():
            st.sidebar.markdown(f"- {row['nombre']} ({row['uso_actual']})")
        
else:
    st.sidebar.markdown("Haz clic en una parcela para ver detalles y actividades.")