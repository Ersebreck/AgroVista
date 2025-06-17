import tempfile, json, os
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import pandas as pd
from .data_simulation import simular_datos, parcelas
from .utils import evaluar_estado_parcelas

load_dotenv()
# Setup Claude 3.5
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = anthropic_key
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)

def preparar_contexto(df_actividades, detalles_df, estado_parcelas_dict):
    with tempfile.NamedTemporaryFile(delete=False, suffix="_act.csv") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix="_det.csv") as f2:
        df_actividades.to_csv(f1.name, index=False)
        detalles_df.to_csv(f2.name, index=False)

    json_data = [{"id": k, "content": " - ".join(v)} for k, v in estado_parcelas_dict.items()]
    with tempfile.NamedTemporaryFile("w", delete=False, suffix="_estado.json", encoding="utf-8") as f3:
        json.dump(json_data, f3, ensure_ascii=False, indent=4)

    docs = CSVLoader(f1.name).load() + CSVLoader(f2.name).load() + \
           JSONLoader(f3.name, jq_schema=".[] | .content", text_content=False).load()

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs_split = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs_split, embeddings)
    return db

def responder_consulta(prompt, db):
    relevant_docs = db.similarity_search(prompt, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    result = llm.invoke([
        {"role": "system", "content": f"""
        Eres un asistente agrícola. Usa el siguiente contexto para ayudar:
        {context}
        """},
        {"role": "user", "content": prompt}
    ])
    return result.content

def generar_contexto_y_responder(prompt: str, df_actividades, detalles_df, estado_parcelas):
    db = preparar_contexto(df_actividades, detalles_df, estado_parcelas)
    return responder_consulta(prompt, db)

if __name__ == "__main__":
    # ejemplo de uso
    actividades, detalles = simular_datos(parcelas)
    estado_parcelas = evaluar_estado_parcelas(actividades)
    contexto = preparar_contexto(actividades, detalles, estado_parcelas)
    prompt = "Cuales parcelas estan activas? Cuales pendientes de intervencion? y cuales inactivas?"
    respuesta = responder_consulta(prompt, contexto)
    print("Respuesta del modelo:\n", respuesta)
    breakpoint()
