import streamlit as st
from streamlit_folium import st_folium
from data_simulation import simular_datos, parcelas_info, parcelas, terrenos
from map import construir_mapa
from views import mostrar_frecuencia, mostrar_detalles, mostrar_ultimas

#
# Inicializa el estado si es necesario
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Buenos días, Juan. Hoy hay 3 parcelas con tareas pendientes, 1 con cosecha reciente, y 1 sin actividad en los últimos 5 días."}]

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
        opciones = ["Frecuencia de actividades", "Detalles de actividad", "Ultimas actividades", "Chat"]
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

    # Mostrar todo el historial
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Escribe tu mensaje"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Respuesta simulada del sistema
        respuesta = f"Simulación de respuesta para: {prompt}"
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
    if respuesta:
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(respuesta)
        respuesta = None
    if st.button("🧹 Limpiar chat"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]


# page footer
    for _ in range(15):
        st.sidebar.markdown("\n", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Desarrollado por:\n**ERICK SEBASTIAN LOZANO ROA 🤖**")