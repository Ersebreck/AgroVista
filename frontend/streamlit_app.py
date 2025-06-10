
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium import GeoJson, GeoJsonTooltip
import altair as alt
import pandas as pd
from datetime import date, timedelta
import random

# ----------------------------
# 1. Datos simulados en memoria

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

# Simulación de actividades con detalles
tipos_actividad = ["Riego", "Fertilización", "Fumigación", "Cosecha", "Siembra", "Limpieza", "Pesaje", "Vacunación", "Ordeño"]
actividades = []

base_date = date(2025, 6, 1)
for parcela_id in parcelas["id"]:
    for _ in range(10):
        tipo = random.choice(tipos_actividad)
        actividades.append({
            "parcela_id": parcela_id,
            "nombre": parcelas[parcelas["id"] == parcela_id]["nombre"].values[0],
            "tipo": tipo,
            "descripcion": "Tarea realizada",
            "fecha": base_date + timedelta(days=random.randint(0, 15))
        })

df_actividades = pd.DataFrame(actividades).reset_index(drop=True)
df_actividades["id"] = df_actividades.index + 1

# ----------------------------
# Detalles por actividad
detalles = []

for actividad in df_actividades.itertuples():
    if actividad.tipo == "Fertilización":
        detalles.append({"actividad_id": actividad.id, "nombre": "Fertilizante NPK", "valor": 50, "unidad": "kg"})
    elif actividad.tipo == "Cosecha":
        detalles.append({"actividad_id": actividad.id, "nombre": "Kg cosechados", "valor": random.randint(800, 1500), "unidad": "kg"})
    elif actividad.tipo == "Riego":
        detalles.append({"actividad_id": actividad.id, "nombre": "Agua utilizada", "valor": random.randint(200, 800), "unidad": "l"})
    elif actividad.tipo == "Pesaje":
        detalles.append({"actividad_id": actividad.id, "nombre": "Peso ganado", "valor": random.randint(300, 600), "unidad": "kg"})
    elif actividad.tipo == "Vacunación":
        detalles.append({"actividad_id": actividad.id, "nombre": "Vacuna aplicada", "valor": "Fiebre Aftosa", "unidad": "dosis"})
    elif actividad.tipo == "Ordeño":
        detalles.append({"actividad_id": actividad.id, "nombre": "Litros ordeñados", "valor": random.randint(10, 30), "unidad": "l"})

detalles_df = pd.DataFrame(detalles)

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

parcelas_ids = {row["nombre"]: row["id"] for _, row in parcelas.iterrows()}

# ----------------------------
# Interfaz de Streamlit
# ----------------------------

st.set_page_config(layout="wide")
st.title("🌱 AgroVista")
st.sidebar.title("📘 Información")

# Crear mapa base
m = folium.Map(location=[4.7110, -74.0721], zoom_start=13)

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

# Polígonos
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
# Mapa + Interacción
# ----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### Mapa interactivo")
    output = st_folium(m, width=700, height=500, return_on_hover=False)

with col2:
    clicked = output["last_object_clicked_tooltip"]
    if clicked:
        clicked = clicked.split("\n")[-2].replace("  ","")
        st.markdown(f"### 📊 {clicked}")

        opciones = ["Frecuencia de actividades", "Detalles de actividad"]
        vista = st.selectbox("Selecciona vista:", opciones)

        if clicked in parcelas_ids:
            df_parcela = df_actividades[df_actividades["nombre"] == clicked]

            if vista == "Frecuencia de actividades":
                freq = df_parcela["tipo"].value_counts()
                st.bar_chart(freq)

            elif vista == "Detalles de actividad":
                ## Merge explícito para asegurar campo 'nombre' de parcela
                df_det = detalles_df.merge(
                    df_parcela[["id", "nombre", "tipo", "fecha"]], 
                    left_on="actividad_id", 
                    right_on="id", 
                    suffixes=("_detalle", "_actividad")
                )
                
                # Convertir a numérico si es posible
                df_det["valor_num"] = pd.to_numeric(df_det["valor"], errors="coerce")

                # Filtrar sólo cuantificables
                df_plot = df_det[df_det["valor_num"].notnull()]
                if not df_plot.empty:            
                    chart = alt.Chart(df_plot).mark_bar().encode(
                        x=alt.X("nombre_detalle:N", title="Detalle"),
                        y=alt.Y("valor_num:Q", title="Valor"),
                        color=alt.Color("tipo:N", title="Actividad"),
                        tooltip=["nombre_detalle", "tipo", "valor", "unidad", "fecha"]
                    ).properties(
                        width=600,
                        height=400,
                        title="🔎 Actividades detalladas cuantificables"
                    )
                    st.write("xdd")
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("No hay detalles numéricos disponibles para graficar esta parcela.")


        else:
            st.markdown("Selecciona una parcela.")
    else:
        st.markdown("Haz clic en una parcela o terreno para ver la visualización.")

# ----------------------------
# Info lateral (sidebar)
# ----------------------------
clicked = output["last_object_clicked_tooltip"]

if clicked:
    clicked = clicked.split("\n")[-2].replace("  ","")
    st.sidebar.markdown(f"### 🏡 {clicked}")
    st.sidebar.markdown(parcelas_info.get(clicked, "Sin información."))

    if clicked in parcelas_ids:
        df_parcela = df_actividades[df_actividades["nombre"] == clicked].sort_values("fecha", ascending=False).head(5)
        st.sidebar.markdown("#### Últimas actividades")
        for _, row in df_parcela.iterrows():
            st.sidebar.markdown(f"- **{row['tipo']}** – {row['fecha'].strftime('%d %b')}")

        st.sidebar.markdown("#### Detalles de actividades")
        ult_ids = df_parcela["id"].values
        detalles_filtrados = detalles_df[detalles_df["actividad_id"].isin(ult_ids)]
        for _, row in detalles_filtrados.iterrows():
            st.sidebar.markdown(f"- {row['nombre']}: **{row['valor']} {row['unidad']}**")

    elif clicked in terrenos["nombre"].values:
        terreno_id = terrenos[terrenos["nombre"] == clicked]["id"].values[0]
        n = parcelas[parcelas["terreno_id"] == terreno_id].shape[0]
        st.sidebar.info(f"Este terreno tiene **{n} parcelas**.")
        parcelas_terreno = parcelas[parcelas["terreno_id"] == terreno_id]
        st.sidebar.markdown(f"#### Parcelas en {clicked}:")
        for _, row in parcelas_terreno.iterrows():
            st.sidebar.markdown(f"- {row['nombre']} ({row['uso_actual']})")
else:
    st.sidebar.markdown("Haz clic en una parcela para ver detalles y actividades.")