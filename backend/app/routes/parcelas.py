from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import SessionLocal
from typing import List

router = APIRouter(
    prefix="/parcelas",
    tags=["Parcelas"]
)

# Dependencia para obtener DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener todas las parcelas
@router.get("/", response_model=List[schemas.ParcelaOut])
def listar_parcelas(db: Session = Depends(get_db)):
    return db.query(models.Parcela).all()

# Obtener parcelas por terreno_id
@router.get("/por-terreno/{terreno_id}", response_model=List[schemas.ParcelaOut])
def listar_parcelas_por_terreno(terreno_id: int, db: Session = Depends(get_db)):
    parcelas = db.query(models.Parcela).filter(models.Parcela.terreno_id == terreno_id).all()
    return parcelas

# Obtener una parcela por ID
@router.get("/{parcela_id}", response_model=schemas.ParcelaOut)
def obtener_parcela(parcela_id: int, db: Session = Depends(get_db)):
    parcela = db.query(models.Parcela).filter(models.Parcela.id == parcela_id).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela no encontrada")
    return parcela

# Crear una nueva parcela
@router.post("/", response_model=schemas.ParcelaOut)
def crear_parcela(parcela: schemas.ParcelaCreate, db: Session = Depends(get_db)):
    nueva_parcela = models.Parcela(**parcela.dict())
    db.add(nueva_parcela)
    db.commit()
    db.refresh(nueva_parcela)
    return nueva_parcela
