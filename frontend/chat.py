import os
import streamlit as st
import pandas as pd
import tempfile
import json
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain.chat_models import init_chat_model
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from data_simulation import simular_datos, parcelas
from utils import evaluar_estado_parcelas
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine


# Soluciona error de Streamlit con torch.classes
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

# Clave API (Claude 3.5)
xd = "sk-ant-api03-iAeS5sqsNsl0A_bxuuJHtu8GuXY"
dx = "dU1-uyRqA4Aj7NHF8x5DoEjwVwELehera5qvpSLiT9sLG1XUyBuo5deZw1g-az96ggAA"
os.environ["ANTHROPIC_API_KEY"] = xd + dx

# Configuración del modelo Claude 3.5
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)

# Prompt actualizado (usa 'summaries' en lugar de 'context')
prompt_template = PromptTemplate(
    input_variables=["summaries", "question"],
    template="""
    Eres un asistente agrícola. Usa el siguiente contexto para responder la pregunta del usuario.

    Contexto:
    {context}

    Pregunta:
    {question}
    """
    )


def preparar_contexto(df_actividades, detalles_df, estado_parcelas_dict):
    # Guardar CSVs temporales
    with tempfile.NamedTemporaryFile(delete=False, suffix="_actividades.csv") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix="_detalles.csv") as f2:
        df_actividades.to_csv(f1.name, index=False)
        detalles_df.to_csv(f2.name, index=False)

    # JSON se escribe y se cierra explícitamente
    contenido_json = [
        {"id": k, "content": " - ".join(v)} for k, v in estado_parcelas_dict.items()
    ]
    with tempfile.NamedTemporaryFile("w", delete=False, suffix="_estado.json", encoding="utf-8") as f3:
        json.dump(contenido_json, f3, ensure_ascii=False, indent=4)
        json_path = f3.name  # guardar ruta

    # Ahora se cargan los archivos
    loader1 = CSVLoader(file_path=f1.name)
    loader2 = CSVLoader(file_path=f2.name)
    loader3 = JSONLoader(
        file_path=json_path,
        jq_schema=".[] | .content",
        text_content=False,
    )

    docs = loader1.load() + loader2.load() + loader3.load()

    # División en chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs_split = text_splitter.split_documents(docs)

    # Embeddings en CPU
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs_split, embeddings)
    return db


def responder_consulta(prompt, db):
    # Construcción moderna del chain de QA con fuentes
    relevant_docs = db.similarity_search(prompt, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    breakpoint()

    result = llm.invoke([
    {
        "role": "system",
        "content": f"""
            You are a data analyst in charged of answering questions about agricultural activities and their details. Be concise and informative.
            Use the following **context** to guide your decision (optional but helpful if relevant):
            {context}
            """
    },
    {"role": "user", "content": prompt}
    ])
    return result.content


def chatbot_structure(df_actividades, detalles_df, estado_parcelas):
    db = preparar_contexto(df_actividades, detalles_df, estado_parcelas)

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
        respuesta = "Simulación"#responder_consulta(prompt, db)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

    if len(st.session_state.messages) > 2:
        if st.button("🧹 Limpiar chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": inicial}]
            st.rerun()




if __name__ == "__main__":
    df_actividades, detalles_df = simular_datos(parcelas)
    estado_parcelas_dict = evaluar_estado_parcelas(df_actividades)
    contexto = preparar_contexto(df_actividades, detalles_df, estado_parcelas_dict)
    resp = responder_consulta("Cuales parcelas estan en estado optimo?", contexto)
    print(resp)