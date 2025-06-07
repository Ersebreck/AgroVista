from fastapi import FastAPI
from app.routes import terrenos, parcelas, ubicaciones, actividades

app = FastAPI()

app.include_router(terrenos.router)
app.include_router(parcelas.router)
app.include_router(ubicaciones.router)
app.include_router(actividades.router)
