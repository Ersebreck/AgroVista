# backend/app/routes/chat.py

from fastapi import APIRouter
from app.schemas import ChatPrompt
from app.chat_logic import generar_contexto_y_responder
from app.data_simulation import simular_datos, parcelas
from app.utils import evaluar_estado_parcelas

router = APIRouter()

@router.post("/chat")
def chat_endpoint(input: ChatPrompt):
    df_actividades, detalles_df = simular_datos(parcelas)
    estado_parcelas = evaluar_estado_parcelas(df_actividades)
    respuesta = generar_contexto_y_responder(input.prompt, df_actividades, detalles_df, estado_parcelas)
    return {"respuesta": respuesta}
