import tempfile, json, os
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
# Setup Claude 3.5
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = anthropic_key
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)

def preparar_contexto(actividades, detalles, estado_parcelas_dict):
    df1 = pd.DataFrame(actividades)
    df2 = pd.DataFrame(detalles)

    with tempfile.NamedTemporaryFile(delete=False, suffix="_act.csv") as f1, \
         tempfile.NamedTemporaryFile(delete=False, suffix="_det.csv") as f2:
        df1.to_csv(f1.name, index=False)
        df2.to_csv(f2.name, index=False)

    contenido_json = [{"id": k, "content": " - ".join(v)} for k, v in estado_parcelas_dict.items()]
    with tempfile.NamedTemporaryFile("w", delete=False, suffix="_estado.json", encoding="utf-8") as f3:
        json.dump(contenido_json, f3, ensure_ascii=False, indent=4)

    docs = CSVLoader(file_path=f1.name).load() + \
           CSVLoader(file_path=f2.name).load() + \
           JSONLoader(file_path=f3.name, jq_schema=".[] | .content", text_content=False).load()

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

if __name__ == "__main__":
    # Ejemplo complejo de uso
    actividades = [
        {"id": 1, "tipo": "Siembra", "fecha": "2023-10-01", "descripcion": "Siembra de maíz", "usuario_id": 1, "parcela_id": 1},
        {"id": 2, "tipo": "Riego", "fecha": "2023-10-02", "descripcion": "Riego de maíz", "usuario_id": 1, "parcela_id": 1}
    ]
    detalles = [
        {"actividad_id": 1, "nombre": "Maíz", "valor": "100 kg", "unidad": "kg"},
        {"actividad_id": 2, "nombre": "Agua", "valor": "500 L", "unidad": "L"}
    ]
    estado_parcelas = {
        "Parcela 1": ["Siembra de maíz", "Riego de maíz"],
        "Parcela 2": ["Preparación del terreno"]
    }
    db = preparar_contexto(actividades, detalles, estado_parcelas)
    prompt = "¿Qué actividades se han realizado en la Parcela 1?"
    respuesta = responder_consulta(prompt, db)
    print(f"Respuesta: {respuesta}")
