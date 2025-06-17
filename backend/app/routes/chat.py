from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.chat_logic import preparar_contexto, responder_consulta
from app.schemas import ChatRequest


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    prompt: str
    actividades: list
    detalles: list
    estado_parcelas: dict

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    contexto = preparar_contexto(request.actividades, request.detalles, request.estado_parcelas)
    respuesta = responder_consulta(request.prompt, contexto)
    return {"respuesta": respuesta}
