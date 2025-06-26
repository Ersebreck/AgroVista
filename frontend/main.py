import streamlit as st
from streamlit_folium import st_folium
from utils import (
    evaluar_estado_parcelas,
    resumen_estado_parcelas,
    cargar_datos
)
from map import construir_mapa
from views import mostrar_frecuencia, mostrar_detalles, mostrar_ultimas
from chat import chatbot_structure
import pandas as pd
import os

os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    html, body {
        font-size: 80%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌱 AgroVista")
hoy = pd.Timestamp.today().normalize()

# ------------------------------
# 🔄 Carga real desde el backend
# ------------------------------

df_actividades, parcelas_df, terrenos_df, parcelas_ids = cargar_datos()

# ------------------------------
# 🗺️ Mapa interactivo
# ------------------------------
col1, col2 = st.columns([5, 4])
with col1:
    st.write("### Mapa interactivo")
    mapa = construir_mapa(df_actividades)
    output = st_folium(mapa, width=600, height=400)

with col2:
    clicked = output.get("last_object_clicked_tooltip")
    if clicked:
        clicked = clicked.split("\n")[-2].replace("  ","")
        st.markdown(f"#### 📊 {clicked}")
        opciones = ["Frecuencia de actividades", "Detalles de actividad", "Ultimas actividades"]

        if clicked in parcelas_ids:
            vista = st.selectbox("Selecciona Gráfico:", opciones)
            df_parcela = df_actividades[df_actividades["nombre"] == clicked]
            if vista == "Frecuencia de actividades":
                mostrar_frecuencia(df_parcela)
            elif vista == "Detalles de actividad":
                mostrar_detalles(df_parcela, pd.DataFrame())  # Puedes conectar detalles reales si haces endpoint
            elif vista == "Ultimas actividades":
                mostrar_ultimas(df_parcela)
        else:
            terreno_id = terrenos_df[terrenos_df["nombre"] == clicked]["id"].values[0]
            parcelas_terreno = parcelas_df[parcelas_df["terreno_id"] == terreno_id]
            with st.expander("📌 Parcelas asociadas:"):
                for _, row in parcelas_terreno.iterrows():
                    nombre = row["nombre"]
                    st.markdown(f"- **{nombre}** ({row['uso_actual']})")
            with st.expander(" 📈 Consolidado"):
                vista = st.selectbox("Selecciona Gráfico:", opciones)
                df_terreno = df_actividades[df_actividades["parcela_id"].isin(parcelas_terreno["id"])]
                mostrar_frecuencia(df_terreno)
    else:
        st.markdown("## Haz clic en una parcela o terreno para ver más información.")

# ------------------------------
# 🤖 Chatbot + resumen de estado
# ------------------------------
st.sidebar.markdown("### 🌱 Chatbot AgroVista", unsafe_allow_html=True)
st.sidebar.markdown("---")

with st.sidebar:
    estado_parcelas = evaluar_estado_parcelas(df_actividades)
    resumen = resumen_estado_parcelas(estado_parcelas)
    inicial = f"RESUMEN ACTUAL: <br> ✅ En estado **óptimo**: {resumen['Óptimo']}<br>" + \
              f"⚠️ Requieren **atención**: {resumen['Atención']}<br>" + \
              f"🚨 En estado **crítico**: {resumen['Crítico']}"

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": inicial}]

    chatbot_structure(df_actividades, pd.DataFrame(), estado_parcelas)

    for _ in range(5):
        st.sidebar.markdown("\n", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Desarrollado por:\n**ERICK SEBASTIAN LOZANO ROA 🤖**")
