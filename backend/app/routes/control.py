from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/control", tags=["Control and KPIs"])


# ---------- CHANGE HISTORY ----------


@router.post("/change/", response_model=schemas.ChangeHistoryOut)
def register_change(
    change: schemas.ChangeHistoryCreate, db: Session = Depends(get_db)
) -> models.ChangeHistory:
    """Register a new change in the change history."""
    db_change = models.ChangeHistory(**change.model_dump())
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    return db_change


@router.get("/change/{id}", response_model=schemas.ChangeHistoryOut)
def get_change(id: int, db: Session = Depends(get_db)) -> models.ChangeHistory:
    """Get a change record by ID."""
    db_change = (
        db.query(models.ChangeHistory).filter(models.ChangeHistory.id == id).first()
    )
    if not db_change:
        raise HTTPException(status_code=404, detail="Change record not found")
    return db_change


@router.get("/changes/", response_model=List[schemas.ChangeHistoryOut])
def list_changes(db: Session = Depends(get_db)) -> List[models.ChangeHistory]:
    """List all change records."""
    return db.query(models.ChangeHistory).all()


# ---------- INDICATORS ----------


@router.post("/indicator/", response_model=schemas.IndicatorOut)
def create_indicator(
    indicator: schemas.IndicatorCreate, db: Session = Depends(get_db)
) -> models.Indicator:
    """Create a new KPI indicator."""
    db_indicator = models.Indicator(**indicator.model_dump())
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator


@router.get("/indicator/{id}", response_model=schemas.IndicatorOut)
def get_indicator(id: int, db: Session = Depends(get_db)) -> models.Indicator:
    """Get an indicator by ID."""
    db_indicator = db.query(models.Indicator).filter(models.Indicator.id == id).first()
    if not db_indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return db_indicator


@router.get("/indicators/", response_model=List[schemas.IndicatorOut])
def list_indicators(db: Session = Depends(get_db)) -> List[models.Indicator]:
    """List all KPI indicators."""
    return db.query(models.Indicator).all()


# ----------------------
# LEGACY ENDPOINTS (Spanish names for backwards compatibility)
# ----------------------


# Change history legacy endpoints
@router.post("/cambio/", response_model=schemas.ChangeHistoryOut)
def registrar_cambio(
    cambio: schemas.ChangeHistoryCreate, db: Session = Depends(get_db)
) -> models.ChangeHistory:
    """Legacy: Register change (Spanish name)."""
    return register_change(cambio, db)


@router.get("/cambio/{id}", response_model=schemas.ChangeHistoryOut)
def obtener_cambio(id: int, db: Session = Depends(get_db)) -> models.ChangeHistory:
    """Legacy: Get change (Spanish name)."""
    return get_change(id, db)


@router.get("/cambios/", response_model=List[schemas.ChangeHistoryOut])
def listar_cambios(db: Session = Depends(get_db)) -> List[models.ChangeHistory]:
    """Legacy: List changes (Spanish name)."""
    return list_changes(db)


# Indicator legacy endpoints
@router.post("/indicador/", response_model=schemas.IndicatorOut)
def crear_indicador(
    indicador: schemas.IndicatorCreate, db: Session = Depends(get_db)
) -> models.Indicator:
    """Legacy: Create indicator (Spanish name)."""
    return create_indicator(indicador, db)


@router.get("/indicador/{id}", response_model=schemas.IndicatorOut)
def obtener_indicador(id: int, db: Session = Depends(get_db)) -> models.Indicator:
    """Legacy: Get indicator (Spanish name)."""
    return get_indicator(id, db)


@router.get("/indicadores/", response_model=List[schemas.IndicatorOut])
def listar_indicadores(db: Session = Depends(get_db)) -> List[models.Indicator]:
    """Legacy: List indicators (Spanish name)."""
    return list_indicators(db)
