from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/", response_model=List[schemas.ActivityOut])
def get_activities(db: Session = Depends(get_db)) -> List[models.Activity]:
    """Get all activities."""
    return db.query(models.Activity).all()


@router.post("/", response_model=schemas.ActivityOut)
def register_activity(
    activity: schemas.ActivityCreate, db: Session = Depends(get_db)
) -> models.Activity:
    """Register a new activity."""
    new_activity = models.Activity(**activity.model_dump())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


@router.get("/{activity_id}", response_model=schemas.ActivityOut)
def get_activity(activity_id: int, db: Session = Depends(get_db)) -> models.Activity:
    """Get a specific activity by ID."""
    activity = (
        db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.put("/{activity_id}", response_model=schemas.ActivityOut)
def update_activity(
    activity_id: int,
    activity_data: schemas.ActivityCreate,
    db: Session = Depends(get_db),
) -> models.Activity:
    """Update an existing activity."""
    activity = (
        db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    for field, value in activity_data.dict(exclude_unset=True).items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete an activity."""
    activity = (
        db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db.delete(activity)
    db.commit()
    return {"message": "Activity deleted successfully"}


@router.get("/by-parcel/{parcel_id}", response_model=List[schemas.ActivityOut])
def list_activities_by_parcel(
    parcel_id: int, db: Session = Depends(get_db)
) -> List[models.Activity]:
    """Get all activities for a specific parcel."""
    return (
        db.query(models.Activity).filter(models.Activity.parcel_id == parcel_id).all()
    )


@router.post("/bulk/", response_model=List[schemas.ActivityOut])
def register_bulk_activities(
    activities: List[schemas.ActivityCreate], db: Session = Depends(get_db)
) -> List[models.Activity]:
    """Register multiple activities at once."""
    new_activities = [models.Activity(**a.model_dump()) for a in activities]
    db.add_all(new_activities)
    db.commit()
    for activity in new_activities:
        db.refresh(activity)
    return new_activities


@router.post("/details/", response_model=List[schemas.ActivityDetailOut])
def register_bulk_activity_details(
    details: List[schemas.ActivityDetailCreate], db: Session = Depends(get_db)
) -> List[models.ActivityDetail]:
    """Register multiple activity details at once."""
    new_details = [models.ActivityDetail(**d.model_dump()) for d in details]
    db.add_all(new_details)
    db.commit()
    for detail in new_details:
        db.refresh(detail)
    return new_details


# Legacy endpoints for backwards compatibility
@router.post("/registrar/", response_model=schemas.ActivityOut)
def registrar_actividad(
    actividad: schemas.ActivityCreate, db: Session = Depends(get_db)
) -> models.Activity:
    """Legacy: Register activity (Spanish name)."""
    return register_activity(actividad, db)


@router.get("/por-parcela/{parcela_id}", response_model=List[schemas.ActivityOut])
def listar_actividades_parcela(
    parcela_id: int, db: Session = Depends(get_db)
) -> List[models.Activity]:
    """Legacy: List activities by parcel (Spanish name)."""
    return list_activities_by_parcel(parcela_id, db)


@router.post("/masivo/", response_model=List[schemas.ActivityOut])
def registrar_actividades_masivo(
    actividades: List[schemas.ActivityCreate], db: Session = Depends(get_db)
) -> List[models.Activity]:
    """Legacy: Register bulk activities (Spanish name)."""
    return register_bulk_activities(actividades, db)


@router.post("/detalles-masivo/", response_model=List[schemas.ActivityDetailOut])
def registrar_detalles_masivo(
    detalles: List[schemas.ActivityDetailCreate], db: Session = Depends(get_db)
) -> List[models.ActivityDetail]:
    """Legacy: Register bulk activity details (Spanish name)."""
    return register_bulk_activity_details(detalles, db)
