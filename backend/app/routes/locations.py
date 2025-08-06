from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

# Conditional imports for geospatial functionality
try:
    from geoalchemy2.shape import to_shape
    from shapely.geometry import mapping

    GEOSPATIAL_ENABLED = True
except ImportError:
    GEOSPATIAL_ENABLED = False

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=schemas.LocationOut)
def create_location(
    location: schemas.LocationCreate, db: Session = Depends(get_db)
) -> models.Location:
    """Create a new location."""
    new_location = models.Location(
        type=location.type,
        coordinates=location.coordinates,  # GeoJSON as raw or serialized dict
        reference=location.reference,
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.get("/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get a location by ID."""
    location = (
        db.query(models.Location).filter(models.Location.id == location_id).first()
    )
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location_to_dict(location)


def location_to_dict(location: models.Location) -> Dict[str, Any]:
    """Convert location model to serializable dictionary."""
    return {
        "id": location.id,
        "type": location.type,
        "coordinates": mapping(to_shape(location.coordinates)),  # Convert to GeoJSON
        "reference": location.reference,
    }


# Legacy endpoints for backwards compatibility
@router.post("/crear", response_model=schemas.LocationOut)
def crear_ubicacion(
    ubicacion: schemas.LocationCreate, db: Session = Depends(get_db)
) -> models.Location:
    """Legacy: Create location (Spanish name)."""
    return create_location(ubicacion, db)


@router.get("/obtener/{ubicacion_id}")
def obtener_ubicacion(
    ubicacion_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Legacy: Get location (Spanish name)."""
    return get_location(ubicacion_id, db)


def ubicacion_to_dict(ubicacion: models.Location) -> Dict[str, Any]:
    """Legacy: Convert location to dict (Spanish name)."""
    return location_to_dict(ubicacion)
