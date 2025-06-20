from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/control", tags=["Control y KPIs"])


# ---------- HISTORIAL CAMBIOS ----------

@router.post("/cambio/", response_model=schemas.HistorialCambioOut)
def registrar_cambio(cambio: schemas.HistorialCambioCreate, db: Session = Depends(get_db)):
    db_cambio = models.HistorialCambio(**cambio.dict())
    db.add(db_cambio)
    db.commit()
    db.refresh(db_cambio)
    return db_cambio

@router.get("/cambio/{id}", response_model=schemas.HistorialCambioOut)
def obtener_cambio(id: int, db: Session = Depends(get_db)):
    db_cambio = db.query(models.HistorialCambio).filter(models.HistorialCambio.id == id).first()
    if not db_cambio:
        raise HTTPException(status_code=404, detail="Cambio no encontrado")
    return db_cambio

@router.get("/cambios/", response_model=list[schemas.HistorialCambioOut])
def listar_cambios(db: Session = Depends(get_db)):
    return db.query(models.HistorialCambio).all()


# ---------- INDICADORES ----------

@router.post("/indicador/", response_model=schemas.IndicadorOut)
def crear_indicador(indicador: schemas.IndicadorCreate, db: Session = Depends(get_db)):
    db_ind = models.Indicador(**indicador.dict())
    db.add(db_ind)
    db.commit()
    db.refresh(db_ind)
    return db_ind

@router.get("/indicador/{id}", response_model=schemas.IndicadorOut)
def obtener_indicador(id: int, db: Session = Depends(get_db)):
    db_ind = db.query(models.Indicador).filter(models.Indicador.id == id).first()
    if not db_ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    return db_ind

@router.get("/indicadores/", response_model=list[schemas.IndicadorOut])
def listar_indicadores(db: Session = Depends(get_db)):
    return db.query(models.Indicador).all()
