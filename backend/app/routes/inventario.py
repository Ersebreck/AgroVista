from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/inventario", tags=["Inventario"])


# ----- INVENTARIO -----

@router.post("/", response_model=schemas.InventarioOut)
def crear_inventario(inventario: schemas.InventarioCreate, db: Session = Depends(get_db)):
    db_inv = models.Inventario(**inventario.dict())
    db.add(db_inv)
    db.commit()
    db.refresh(db_inv)
    return db_inv

@router.get("/{id}", response_model=schemas.InventarioOut)
def obtener_inventario(id: int, db: Session = Depends(get_db)):
    db_inv = db.query(models.Inventario).filter(models.Inventario.id == id).first()
    if not db_inv:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return db_inv

@router.get("/", response_model=list[schemas.InventarioOut])
def listar_inventarios(db: Session = Depends(get_db)):
    return db.query(models.Inventario).all()


# ----- EVENTO INVENTARIO -----

@router.post("/evento/", response_model=schemas.EventoInventarioOut)
def crear_evento_inventario(evento: schemas.EventoInventarioCreate, db: Session = Depends(get_db)):
    db_evento = models.EventoInventario(**evento.dict())
    db.add(db_evento)

    # Actualiza inventario según el tipo de movimiento
    inventario = db.query(models.Inventario).filter(models.Inventario.id == evento.inventario_id).first()
    if not inventario:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    if evento.tipo_movimiento == "entrada":
        inventario.cantidad_actual += evento.cantidad
    elif evento.tipo_movimiento == "salida":
        inventario.cantidad_actual -= evento.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido (entrada/salida)")

    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/evento/{id}", response_model=schemas.EventoInventarioOut)
def obtener_evento(id: int, db: Session = Depends(get_db)):
    db_evento = db.query(models.EventoInventario).filter(models.EventoInventario.id == id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return db_evento

@router.get("/eventos/", response_model=list[schemas.EventoInventarioOut])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.EventoInventario).all()
