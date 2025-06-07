from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import SessionLocal
from typing import List

router = APIRouter(
    prefix="/actividades",
    tags=["Actividades"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ActividadOut)
def registrar_actividad(actividad: schemas.ActividadCreate, db: Session = Depends(get_db)):
    nueva = models.Actividad(**actividad.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/por-parcela/{parcela_id}", response_model=List[schemas.ActividadOut])
def listar_actividades_parcela(parcela_id: int, db: Session = Depends(get_db)):
    return db.query(models.Actividad).filter(models.Actividad.parcela_id == parcela_id).all()
