import streamlit as st
from streamlit_folium import st_folium
from data_simulation import simular_datos, parcelas_info, parcelas, terrenos
from map import construir_mapa
from views import mostrar_frecuencia, mostrar_detalles, mostrar_ultimas
from utils import chatbot_response
#
# Inicializa el estado si es necesario

hola = "Buenos días, Juan. Hoy hay 3 parcelas con tareas pendientes, 1 con cosecha reciente, y 1 sin actividad en los últimos 5 días."

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": hola}]

st.set_page_config(layout="wide")
st.title("🌱 AgroVista")
# Carga de datos
df_actividades, detalles_df = simular_datos(parcelas)
parcelas_ids = {row["nombre"]: row["id"] for _, row in parcelas.iterrows()}

# Mapa
col1, col2 = st.columns([2, 1])
with col1:
    st.write("### Mapa interactivo")
    mapa = construir_mapa()
    output = st_folium(mapa, width=700, height=500)

with col2:
    clicked = output.get("last_object_clicked_tooltip")
    if clicked:
        clicked = clicked.split("\n")[-2].replace("  ","")
        st.markdown(f"### 📊 {clicked}")
        st.write(parcelas_info.get(clicked, "Sin información."))
        opciones = ["Frecuencia de actividades", "Detalles de actividad", "Ultimas actividades"]
        vista = st.selectbox("Selecciona vista:", opciones)

        if clicked in parcelas_ids:
            df_parcela = df_actividades[df_actividades["nombre"] == clicked]
            if vista == "Frecuencia de actividades":
                mostrar_frecuencia(df_parcela)
            elif vista == "Detalles de actividad":
                mostrar_detalles(df_parcela, detalles_df)
            elif vista == "Ultimas actividades":
                mostrar_ultimas(df_parcela)
     
        else:
            st.info("Selecciona una parcela.")
    else:
        st.markdown("# Haz clic en una parcela o terreno para ver más información.")

# sidebar
st.sidebar.header("🌱 AgroVista")
# Información del usuario
#usuario = st.sidebar.selectbox("Selecciona un usuario:", ["Escoger Un Usuario","Propietario", "Administrador", "Operario"])

with st.sidebar:

    chatbot_response()
    st.sidebar.markdown("---")


# page footer
    for _ in range(13):
        st.sidebar.markdown("\n", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Desarrollado por:\n**ERICK SEBASTIAN LOZANO ROA 🤖**")