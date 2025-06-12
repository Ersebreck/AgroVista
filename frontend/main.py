import streamlit as st
from streamlit_folium import st_folium
from data_simulation import simular_datos, parcelas_info, parcelas, terrenos
from map import construir_mapa
from views import mostrar_frecuencia, mostrar_detalles, mostrar_ultimas
from utils import evaluar_estado_parcelas, resumen_estado_parcelas
from chat import chatbot_structure
import pandas as pd
import os

os.environ["STREAMLIT_WATCHER_TYPE"] = "none"


# Configuración de la página
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    html, body {
        font-size: 80%;
    }
    </style>
""", unsafe_allow_html=True)

hoy = pd.Timestamp.today().normalize()

st.title("🌱 AgroVista")

# Carga de datos
df_actividades, detalles_df = simular_datos(parcelas)
parcelas_ids = {row["nombre"]: row["id"] for _, row in parcelas.iterrows()}

# Mapa
col1, col2 = st.columns([5,4])
with col1:
    st.write("### Mapa interactivo")
    mapa = construir_mapa(df_actividades)
    output = st_folium(mapa, width=600, height=400)

with col2:
    clicked = output.get("last_object_clicked_tooltip")
    if clicked:
        clicked = clicked.split("\n")[-2].replace("  ","")
        st.markdown(f"#### 📊 {clicked} - {(parcelas_info.get(clicked, 'Sin información.'))}")
        opciones = ["Frecuencia de actividades", "Detalles de actividad", "Ultimas actividades"]
        

        if clicked in parcelas_ids:
            vista = st.selectbox("Selecciona Gráfico:", opciones)
            df_parcela = df_actividades[df_actividades["nombre"] == clicked]
            if vista == "Frecuencia de actividades":
                mostrar_frecuencia(df_parcela)
            elif vista == "Detalles de actividad":
                mostrar_detalles(df_parcela, detalles_df)
            elif vista == "Ultimas actividades":
                mostrar_ultimas(df_parcela)
     
        else:
            # Si es un Terreno, mostrar consolidado de sus parcelas
            terreno_id = terrenos[terrenos["nombre"] == clicked]["id"].values[0]
            parcelas_terreno = parcelas[parcelas["terreno_id"] == terreno_id]
            with st.expander("📌 Parcelas asociadas:"):
                for _, row in parcelas_terreno.iterrows():
                    nombre = row["nombre"]
                    st.markdown(f"- **{nombre}** ({row['uso_actual']})")
                
                df_terreno = df_actividades[df_actividades["parcela_id"].isin(parcelas_terreno["id"])]

            with st.expander(" 📈 Consolidado"):
                vista = st.selectbox("Selecciona Gráfico:", opciones)
                mostrar_frecuencia(df_terreno)
    else:
        st.markdown("## Haz clic en una parcela o terreno para ver más información.")



# sidebar
st.sidebar.markdown("### 🌱 Chatbot AgroVista")
st.sidebar.markdown("---")
with st.sidebar:
    estado_parcelas = evaluar_estado_parcelas(df_actividades)
    resumen = resumen_estado_parcelas(estado_parcelas)
    inicial = f"RESUMEN ACTUAL: <br> ✅ En estado **óptimo**: {resumen['Óptimo']}<br>" + f"⚠️ Requieren **atención**: {resumen['Atención']}<br>" + f"🚨 En estado **crítico**: {resumen['Crítico']}"

    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": inicial}]

    chatbot_structure(df_actividades, detalles_df)

    


# page footer
    for _ in range(5):
        st.sidebar.markdown("\n", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Desarrollado por:\n**ERICK SEBASTIAN LOZANO ROA 🤖**")