import json
import os
import tempfile
from typing import Dict, List

import pandas as pd
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.data_simulation import parcels, simulate_data
from app.utils import evaluate_parcel_status

# Load environment variables and setup Claude 3.5
load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)
else:
    llm = None


def prepare_context(
    activities_df: pd.DataFrame,
    details_df: pd.DataFrame,
    parcel_status_dict: Dict[int, List[str]],
) -> FAISS:
    """
    Prepare context for agricultural chat assistant.

    Args:
        activities_df: DataFrame containing activity data
        details_df: DataFrame containing activity details
        parcel_status_dict: Dictionary mapping parcel_id to status list

    Returns:
        FAISS vector database with embedded context
    """
    # Create temporary CSV files for activities and details
    with (
        tempfile.NamedTemporaryFile(delete=False, suffix="_activities.csv") as f1,
        tempfile.NamedTemporaryFile(delete=False, suffix="_details.csv") as f2,
    ):
        activities_df.to_csv(f1.name, index=False)
        details_df.to_csv(f2.name, index=False)

    # Create JSON data for parcel status
    json_data = [
        {"id": k, "content": " - ".join(v)} for k, v in parcel_status_dict.items()
    ]
    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix="_status.json", encoding="utf-8"
    ) as f3:
        json.dump(json_data, f3, ensure_ascii=False, indent=4)

    # Load documents from files
    docs = (
        CSVLoader(f1.name).load()
        + CSVLoader(f2.name).load()
        + JSONLoader(f3.name, jq_schema=".[] | .content", text_content=False).load()
    )

    # Split documents into chunks
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs_split = splitter.split_documents(docs)

    # Create embeddings and vector database
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = FAISS.from_documents(docs_split, embeddings)
    return db


def answer_query(prompt: str, db: FAISS) -> str:
    """
    Generate answer for agricultural query using context database.

    Args:
        prompt: User query/prompt
        db: FAISS vector database with context

    Returns:
        AI-generated response string
    """
    if llm is None:
        return "AI assistant unavailable - ANTHROPIC_API_KEY not configured"

    relevant_docs = db.similarity_search(prompt, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    result = llm.invoke(
        [
            {
                "role": "system",
                "content": f"""
        You are an agricultural assistant. Use the following context to help:
        {context}
        
        Provide helpful, accurate agricultural advice based on the data provided.
        Focus on practical recommendations for farm management.
        """,
            },
            {"role": "user", "content": prompt},
        ]
    )
    return result.content


def generate_context_and_respond(
    prompt: str,
    activities_df: pd.DataFrame,
    details_df: pd.DataFrame,
    parcel_status: Dict[int, List[str]],
) -> str:
    """
    Complete pipeline to generate agricultural assistant response.

    Args:
        prompt: User query
        activities_df: Activities data
        details_df: Activity details data
        parcel_status: Parcel status information

    Returns:
        AI-generated response string
    """
    db = prepare_context(activities_df, details_df, parcel_status)
    return answer_query(prompt, db)


# Legacy function names for backwards compatibility
def preparar_contexto(
    df_actividades: pd.DataFrame,
    detalles_df: pd.DataFrame,
    estado_parcelas_dict: Dict[int, List[str]],
) -> FAISS:
    """Legacy wrapper for prepare_context"""
    return prepare_context(df_actividades, detalles_df, estado_parcelas_dict)


def responder_consulta(prompt: str, db: FAISS) -> str:
    """Legacy wrapper for answer_query"""
    return answer_query(prompt, db)


def generar_contexto_y_responder(
    prompt: str,
    df_actividades: pd.DataFrame,
    detalles_df: pd.DataFrame,
    estado_parcelas: Dict[int, List[str]],
) -> str:
    """Legacy wrapper for generate_context_and_respond"""
    return generate_context_and_respond(
        prompt, df_actividades, detalles_df, estado_parcelas
    )


if __name__ == "__main__":
    # Example usage
    activities, details = simulate_data(parcels)
    parcel_status = evaluate_parcel_status(activities)
    context = prepare_context(activities, details, parcel_status)
    prompt = "Which parcels are active? Which are pending intervention? And which are inactive?"
    response = answer_query(prompt, context)
    print("Model response:\n", response)
    breakpoint()
