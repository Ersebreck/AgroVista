from typing import Dict

from fastapi import APIRouter

from app.chat_logic import generate_context_and_respond
from app.data_simulation import parcels, simulate_data
from app.schemas import ChatRequest
from app.utils import evaluate_parcel_status

router = APIRouter()


@router.post("/chat")
def chat_endpoint(chat_input: ChatRequest) -> Dict[str, str]:
    """
    Chat endpoint for AI assistant interactions.

    Args:
        chat_input: Request containing the user prompt

    Returns:
        Dictionary containing the AI response
    """
    activities_df, details_df = simulate_data(parcels)
    parcel_status = evaluate_parcel_status(activities_df)
    response = generate_context_and_respond(
        chat_input.prompt, activities_df, details_df, parcel_status
    )
    return {"response": response}


# Legacy response format for backwards compatibility
def get_chat_response_legacy(chat_input: ChatRequest) -> Dict[str, str]:
    """Get chat response with legacy Spanish key."""
    result = chat_endpoint(chat_input)
    return {"respuesta": result["response"]}
