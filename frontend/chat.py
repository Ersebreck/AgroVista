import streamlit as st
from utils import obtener_respuesta_llm

def chatbot_structure(df_actividades, detalles_df, estado_parcelas):
    estado_parcelas = {
        "Óptimo": sum("Activa" in str(x) for x in df_actividades.tipo),
        "Atención": 1,
        "Crítico": 1
    }

    inicial = f"""
    RESUMEN ACTUAL: <br> 
    🌿 En estado <b>óptimo</b>: {estado_parcelas['Óptimo']}<br>
    ⚠️ Requieren <b>atención</b>: {estado_parcelas['Atención']}<br>
    🔥 En estado <b>crítico</b>: {estado_parcelas['Crítico']}
    """

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": inicial}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Chatea con AgroVista"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        respuesta = obtener_respuesta_llm(prompt)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

    if len(st.session_state.messages) > 2:
        if st.button("🧹 Limpiar chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": inicial}]
            st.rerun()