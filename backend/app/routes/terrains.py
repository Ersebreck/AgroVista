from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/terrains", tags=["Terrains"])


@router.get("/", response_model=List[schemas.TerrainOut])
def list_terrains(db: Session = Depends(get_db)) -> List[models.Terrain]:
    """Get all terrains."""
    return db.query(models.Terrain).all()


@router.get("/{terrain_id}", response_model=schemas.TerrainOut)
def get_terrain(terrain_id: int, db: Session = Depends(get_db)) -> models.Terrain:
    """Get a terrain by ID."""
    terrain = db.query(models.Terrain).filter(models.Terrain.id == terrain_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain not found")
    return terrain


@router.post("/", response_model=schemas.TerrainOut)
def create_terrain(
    terrain: schemas.TerrainCreate, db: Session = Depends(get_db)
) -> models.Terrain:
    """Create new terrain."""
    new_terrain = models.Terrain(**terrain.model_dump())
    db.add(new_terrain)
    db.commit()
    db.refresh(new_terrain)
    return new_terrain


# Legacy endpoints for backwards compatibility
@router.get("/listar", response_model=List[schemas.TerrainOut])
def listar_terrenos(db: Session = Depends(get_db)) -> List[models.Terrain]:
    """Legacy: Get all terrains (Spanish name)."""
    return list_terrains(db)


@router.get("/obtener/{terreno_id}", response_model=schemas.TerrainOut)
def obtener_terreno(terreno_id: int, db: Session = Depends(get_db)) -> models.Terrain:
    """Legacy: Get terrain by ID (Spanish name)."""
    return get_terrain(terreno_id, db)


@router.post("/crear", response_model=schemas.TerrainOut)
def crear_terreno(
    terreno: schemas.TerrainCreate, db: Session = Depends(get_db)
) -> models.Terrain:
    """Legacy: Create terrain (Spanish name)."""
    return create_terrain(terreno, db)
