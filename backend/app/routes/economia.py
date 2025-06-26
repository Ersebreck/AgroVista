from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from sqlalchemy import func

router = APIRouter(prefix="/economia", tags=["Economía"])


# ----- TRANSACCIONES -----

@router.post("/transaccion/", response_model=schemas.TransaccionOut)
def crear_transaccion(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = models.Transaccion(**transaccion.dict())
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.get("/transaccion/{id}", response_model=schemas.TransaccionOut)
def obtener_transaccion(id: int, db: Session = Depends(get_db)):
    db_transaccion = db.query(models.Transaccion).filter(models.Transaccion.id == id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return db_transaccion

@router.get("/transacciones/", response_model=list[schemas.TransaccionOut])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(models.Transaccion).all()


# ----- PRESUPUESTOS -----

@router.post("/presupuesto/", response_model=schemas.PresupuestoOut)
def crear_presupuesto(presupuesto: schemas.PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = models.Presupuesto(**presupuesto.dict())
    db.add(db_presupuesto)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@router.get("/presupuesto/{id}", response_model=schemas.PresupuestoOut)
def obtener_presupuesto(id: int, db: Session = Depends(get_db)):
    db_presupuesto = db.query(models.Presupuesto).filter(models.Presupuesto.id == id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return db_presupuesto

@router.get("/presupuestos/", response_model=list[schemas.PresupuestoOut])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(models.Presupuesto).all()


@router.get("/comparativo/")
def comparativo_presupuesto_vs_real(
    anio: int = Query(..., description="Año del análisis"),
    parcela_id: int = Query(None, description="Filtrar por parcela"),
    db: Session = Depends(get_db)
):
    # PRESUPUESTO agrupado por categoría
    presupuesto_query = db.query(
        models.Presupuesto.categoria,
        func.sum(models.Presupuesto.monto_estimado).label("monto_presupuestado")
    ).filter(models.Presupuesto.anio == anio)

    if parcela_id:
        presupuesto_query = presupuesto_query.filter(models.Presupuesto.parcela_id == parcela_id)

    presupuesto_data = {
        row.categoria: row.monto_presupuestado
        for row in presupuesto_query.group_by(models.Presupuesto.categoria).all()
    }

    # TRANSACCIONES agrupadas por categoría
    transaccion_query = db.query(
        models.Transaccion.categoria,
        func.sum(models.Transaccion.monto).label("monto_ejecutado")
    ).filter(
        func.extract("year", models.Transaccion.fecha) == anio,
        models.Transaccion.tipo == "gasto"
    )

    if parcela_id:
        transaccion_query = transaccion_query.filter(models.Transaccion.parcela_id == parcela_id)

    transaccion_data = {
        row.categoria: row.monto_ejecutado
        for row in transaccion_query.group_by(models.Transaccion.categoria).all()
    }

    # Unir resultados
    categorias = set(presupuesto_data.keys()).union(transaccion_data.keys())
    resultado = []
    for categoria in categorias:
        plan = presupuesto_data.get(categoria, 0.0)
        real = transaccion_data.get(categoria, 0.0)
        diferencia = plan - real
        alerta = abs(diferencia) > (0.15 * plan) if plan > 0 else False

        resultado.append({
            "categoria": categoria,
            "monto_presupuestado": round(plan, 2),
            "monto_ejecutado": round(real, 2),
            "diferencia": round(diferencia, 2),
            "alerta": alerta
        })

    return resultado

@router.get("/resumen-global/")
def resumen_economico_global(
    anio: int = Query(..., description="Año del análisis"),
    parcela_id: int = Query(None, description="Filtrar por parcela"),
    db: Session = Depends(get_db)
):
    models.Presupuesto_query = db.query(func.sum(models.Presupuesto.monto_estimado)).filter(models.Presupuesto.anio == anio)
    models.Transaccion_query = db.query(func.sum(models.Transaccion.monto)).filter(
        func.extract("year", models.Transaccion.fecha) == anio,
        models.Transaccion.tipo == "gasto"
    )

    if parcela_id:
        models.Presupuesto_query = models.Presupuesto_query.filter(models.Presupuesto.parcela_id == parcela_id)
        models.Transaccion_query = models.Transaccion_query.filter(models.Transaccion.parcela_id == parcela_id)

    models.Presupuesto_total = models.Presupuesto_query.scalar() or 0.0
    ejecutado_total = models.Transaccion_query.scalar() or 0.0
    diferencia = models.Presupuesto_total - ejecutado_total
    alerta_global = abs(diferencia) > (0.15 * models.Presupuesto_total) if models.Presupuesto_total > 0 else False

    return {
        "models.Presupuesto_total": round(models.Presupuesto_total, 2),
        "ejecutado_total": round(ejecutado_total, 2),
        "diferencia_total": round(diferencia, 2),
        "alerta_global": alerta_global
    }

@router.get("/comparativo-mensual/")
def comparativo_mensual(
    anio: int = Query(...),
    categoria: str = Query(None),
    parcela_id: int = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        func.extract("month", models.Transaccion.fecha).label("mes"),
        func.sum(models.Transaccion.monto).label("monto_ejecutado")
    ).filter(
        func.extract("year", models.Transaccion.fecha) == anio,
        models.Transaccion.tipo == "gasto"
    )

    if categoria:
        query = query.filter(models.Transaccion.categoria == categoria)
    if parcela_id:
        query = query.filter(models.Transaccion.parcela_id == parcela_id)

    query = query.group_by(func.extract("month", models.Transaccion.fecha)).order_by("mes")

    return [
        {
            "mes": int(row.mes),
            "monto_ejecutado": round(row.monto_ejecutado, 2)
        }
        for row in query.all()
    ]
