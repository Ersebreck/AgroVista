from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import SessionLocal
from typing import List

router = APIRouter(
    prefix="/ubicaciones",
    tags=["Ubicaciones"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.UbicacionOut)
def crear_ubicacion(ubicacion: schemas.UbicacionCreate, db: Session = Depends(get_db)):
    nueva_ubicacion = models.Ubicacion(
        tipo=ubicacion.tipo,
        coordenadas=ubicacion.coordenadas,  # GeoJSON como dict crudo o serializado
        referencia=ubicacion.referencia
    )
    db.add(nueva_ubicacion)
    db.commit()
    db.refresh(nueva_ubicacion)
    return nueva_ubicacion

@router.get("/{ubicacion_id}", response_model=schemas.UbicacionOut)
def obtener_ubicacion(ubicacion_id: int, db: Session = Depends(get_db)):
    ubicacion = db.query(models.Ubicacion).filter(models.Ubicacion.id == ubicacion_id).first()
    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return ubicacion
