from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import SessionLocal
from typing import List

router = APIRouter(
    prefix="/terrenos",
    tags=["Terrenos"]
)

# Dependencia para obtener DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener todos los terrenos
@router.get("/", response_model=List[schemas.TerrenoOut])
def listar_terrenos(db: Session = Depends(get_db)):
    return db.query(models.Terreno).all()

# Obtener un terreno por ID
@router.get("/{terreno_id}", response_model=schemas.TerrenoOut)
def obtener_terreno(terreno_id: int, db: Session = Depends(get_db)):
    terreno = db.query(models.Terreno).filter(models.Terreno.id == terreno_id).first()
    if not terreno:
        raise HTTPException(status_code=404, detail="Terreno no encontrado")
    return terreno

# Crear nuevo terreno
@router.post("/", response_model=schemas.TerrenoOut)
def crear_terreno(terreno: schemas.TerrenoCreate, db: Session = Depends(get_db)):
    nuevo_terreno = models.Terreno(**terreno.dict())
    db.add(nuevo_terreno)
    db.commit()
    db.refresh(nuevo_terreno)
    return nuevo_terreno
