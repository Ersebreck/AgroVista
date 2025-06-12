from pandasai_litellm import LiteLLM
import streamlit as st
import pandasai as pai
from utils import evaluar_estado_parcelas, resumen_estado_parcelas
import os

xd = "sk-ant-api03-iAeS5sqsNsl0A_bxuuJHtu8GuXY"
dx = "dU1-uyRqA4Aj7NHF8x5DoEjwVwELehera5qvpSLiT9sLG1XUyBuo5deZw1g-az96ggAA"
os.environ["ANTHROPIC_API_KEY"] = xd+dx

def chatbot_response(prompt, df_actividades, detalles_df):
    df_actividades_smart = pai.DataFrame(df_actividades)
    df_detalles_smart = pai.DataFrame(detalles_df)
    llm = LiteLLM(model="anthropic:claude-3-5-sonnet-latest",temperature=0) 
    pai.config.set("llm", llm)
    pai.config.set("verbose", True)
    pai.config.set("temperature", 0)
    pai.config.set("seed", 888)
    try:
        response = pai.chat(
            prompt,
            df_actividades_smart,
            df_detalles_smart
        )
        return str(response)
    except Exception as e:
        return f"Error al generar respuesta: {e}"


def chatbot_structure(df_actividades, detalles_df):
    estado_parcelas = evaluar_estado_parcelas(df_actividades)
    resumen = resumen_estado_parcelas(estado_parcelas)
    inicial = f"RESUMEN ACTUAL: <br> 🌿 En estado **óptimo**: {resumen['Óptimo']}<br>" + f"⚠️ Requieren **atención**: {resumen['Atención']}<br>" + f"🔥 En estado **crítico**: {resumen['Crítico']}"


    # Mostrar todo el historial
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

    # Entrada del usuario
    if prompt := st.chat_input("Chatea con AgroVista"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Respuesta del chatbot
        respuesta = chatbot_response(prompt, df_actividades, detalles_df)

        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()
    if len(st.session_state.messages)>2:
        if st.button("🧹 Limpiar chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": inicial}]
            st.rerun()