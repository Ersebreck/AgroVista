import os
import streamlit as st
import pandas as pd
import tempfile

from langchain_community.document_loaders import CSVLoader
from langchain.chat_models import init_chat_model
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


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
{summaries}

Pregunta:
{question}
"""
)


def preparar_contexto(df_actividades, detalles_df):
    # Guardar CSVs temporales
    with tempfile.NamedTemporaryFile(delete=False, suffix="_actividades.csv") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix="_detalles.csv") as f2:
        df_actividades.to_csv(f1.name, index=False)
        detalles_df.to_csv(f2.name, index=False)

        loader1 = CSVLoader(file_path=f1.name)
        loader2 = CSVLoader(file_path=f2.name)

        docs = loader1.load() + loader2.load()

    # División en chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs_split = text_splitter.split_documents(docs)

    # Embeddings en CPU
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    db = FAISS.from_documents(docs_split, embeddings)
    return db


def responder_consulta(prompt, db):
    # Construcción moderna del chain de QA con fuentes
    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=prompt_template)
    qa_chain = RetrievalQAWithSourcesChain(
        combine_documents_chain=stuff_chain,
        retriever=db.as_retriever()
    )

    respuesta = qa_chain.invoke({"question": prompt})
    return respuesta["answer"]


def chatbot_structure(df_actividades, detalles_df):
    db = preparar_contexto(df_actividades, detalles_df)

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
        respuesta = responder_consulta(prompt, db)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})
        st.rerun()

    if len(st.session_state.messages) > 2:
        if st.button("🧹 Limpiar chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": inicial}]
            st.rerun()
