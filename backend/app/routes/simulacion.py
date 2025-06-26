from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from datetime import date


router = APIRouter(prefix="/simulacion", tags=["Simulación"])


# ----- SIMULACIONES -----

@router.post("/", response_model=schemas.SimulacionOut)
def crear_simulacion(simulacion: schemas.SimulacionCreate, db: Session = Depends(get_db)):
    db_sim = models.Simulacion(**simulacion.dict())
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    return db_sim

@router.get("/{id}", response_model=schemas.SimulacionOut)
def obtener_simulacion(id: int, db: Session = Depends(get_db)):
    db_sim = db.query(models.Simulacion).filter(models.Simulacion.id == id).first()
    if not db_sim:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    return db_sim

@router.get("/", response_model=list[schemas.SimulacionOut])
def listar_simulaciones(db: Session = Depends(get_db)):
    return db.query(models.Simulacion).all()


# ----- PARÁMETROS BIOLÓGICOS -----

@router.post("/parametro/", response_model=schemas.ParametroBiologicoOut)
def crear_parametro(param: schemas.ParametroBiologicoCreate, db: Session = Depends(get_db)):
    db_param = models.ParametroBiologico(**param.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param

@router.get("/parametro/{id}", response_model=schemas.ParametroBiologicoOut)
def obtener_parametro(id: int, db: Session = Depends(get_db)):
    db_param = db.query(models.ParametroBiologico).filter(models.ParametroBiologico.id == id).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return db_param

@router.get("/parametros/", response_model=list[schemas.ParametroBiologicoOut])
def listar_parametros(db: Session = Depends(get_db)):
    return db.query(models.ParametroBiologico).all()





def simular_crecimiento(anio_inicio, anios, unidad_inicial, tasas):
    resultados = {}
    actual = unidad_inicial
    for i in range(anios):
        anio = anio_inicio + i
        nacimientos = actual * tasas.get("natalidad", 0)
        ventas = actual * tasas.get("venta", 0)
        muertes = actual * tasas.get("mortalidad", 0)
        actual = actual + nacimientos - ventas - muertes
        resultados[anio] = round(actual, 2)
    return resultados


@router.post("/simular")
def simular_proyeccion(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    anio_inicio = payload["anio_inicio"]
    anios = payload["anios"]
    unidad_inicial = payload["unidad_inicial"]
    tasas = payload.get("tasas", {})
    guardar = payload.get("guardar", False)
    nombre = payload.get("nombre", f"Simulación {date.today()}")
    usuario_id = payload.get("usuario_id", 1)

    resultados = simular_crecimiento(anio_inicio, anios, unidad_inicial, tasas)

    if guardar:
        sim = models.Simulacion(
            nombre=nombre,
            descripcion="Simulación automática",
            fecha_creacion=date.today(),
            parametros=tasas,
            resultados=resultados,
            usuario_id=usuario_id
        )
        db.add(sim)
        db.commit()

    return {"resultados": resultados}

