from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.get("/", response_model=List[schemas.ParcelOut])
def list_parcels(db: Session = Depends(get_db)) -> List[models.Parcel]:
    """Get all parcels."""
    return db.query(models.Parcel).all()


@router.get("/by-terrain/{terrain_id}", response_model=List[schemas.ParcelOut])
def list_parcels_by_terrain(
    terrain_id: int, db: Session = Depends(get_db)
) -> List[models.Parcel]:
    """Get parcels by terrain ID."""
    parcels = (
        db.query(models.Parcel).filter(models.Parcel.terrain_id == terrain_id).all()
    )
    return parcels


@router.get("/{parcel_id}", response_model=schemas.ParcelOut)
def get_parcel(parcel_id: int, db: Session = Depends(get_db)) -> models.Parcel:
    """Get a parcel by ID."""
    parcel = db.query(models.Parcel).filter(models.Parcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel


@router.post("/", response_model=schemas.ParcelOut)
def create_parcel(
    parcel: schemas.ParcelCreate, db: Session = Depends(get_db)
) -> models.Parcel:
    """Create a new parcel."""
    new_parcel = models.Parcel(**parcel.model_dump())
    db.add(new_parcel)
    db.commit()
    db.refresh(new_parcel)
    return new_parcel


# Legacy endpoints for backwards compatibility
@router.get("/listar", response_model=List[schemas.ParcelOut])
def listar_parcelas(db: Session = Depends(get_db)) -> List[models.Parcel]:
    """Legacy: Get all parcels (Spanish name)."""
    return list_parcels(db)


@router.get("/listar-por-terreno/{terreno_id}", response_model=List[schemas.ParcelOut])
def listar_parcelas_por_terreno(
    terreno_id: int, db: Session = Depends(get_db)
) -> List[models.Parcel]:
    """Legacy: Get parcels by terrain (Spanish name)."""
    return list_parcels_by_terrain(terreno_id, db)


@router.get("/obtener/{parcela_id}", response_model=schemas.ParcelOut)
def obtener_parcela(parcela_id: int, db: Session = Depends(get_db)) -> models.Parcel:
    """Legacy: Get parcel by ID (Spanish name)."""
    return get_parcel(parcela_id, db)


@router.post("/crear", response_model=schemas.ParcelOut)
def crear_parcela(
    parcela: schemas.ParcelCreate, db: Session = Depends(get_db)
) -> models.Parcel:
    """Legacy: Create parcel (Spanish name)."""
    return create_parcel(parcela, db)
