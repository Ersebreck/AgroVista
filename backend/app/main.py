from fastapi import FastAPI
from app.routes import terrenos, parcelas, ubicaciones, actividades, chat

app = FastAPI()

app.include_router(terrenos.router)
app.include_router(parcelas.router)
app.include_router(ubicaciones.router)
app.include_router(actividades.router)
app.include_router(chat.router)
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de AgroVista. Usa los endpoints para interactuar con los datos agrícolas."}
