from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ----- INVENTORY -----


@router.post("/", response_model=schemas.InventoryOut)
def create_inventory(
    inventory: schemas.InventoryCreate, db: Session = Depends(get_db)
) -> models.Inventory:
    """Create a new inventory item."""
    db_inventory = models.Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/{id}", response_model=schemas.InventoryOut)
def get_inventory(id: int, db: Session = Depends(get_db)) -> models.Inventory:
    """Get an inventory item by ID."""
    db_inventory = db.query(models.Inventory).filter(models.Inventory.id == id).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory


@router.get("/", response_model=List[schemas.InventoryOut])
def list_inventories(db: Session = Depends(get_db)) -> List[models.Inventory]:
    """List all inventory items."""
    return db.query(models.Inventory).all()


# ----- INVENTORY EVENTS -----


@router.post("/event/", response_model=schemas.InventoryEventOut)
def create_inventory_event(
    event: schemas.InventoryEventCreate, db: Session = Depends(get_db)
) -> models.InventoryEvent:
    """Create a new inventory movement event."""
    db_event = models.InventoryEvent(**event.model_dump())
    db.add(db_event)

    # Update inventory according to movement type
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.id == event.inventory_id)
        .first()
    )
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if event.movement_type == "inflow":
        inventory.current_quantity += event.quantity
    elif event.movement_type == "outflow":
        inventory.current_quantity -= event.quantity
    else:
        raise HTTPException(
            status_code=400, detail="Invalid movement type (inflow/outflow)"
        )

    db.commit()
    db.refresh(db_event)
    return db_event


@router.get("/event/{id}", response_model=schemas.InventoryEventOut)
def get_inventory_event(
    id: int, db: Session = Depends(get_db)
) -> models.InventoryEvent:
    """Get an inventory event by ID."""
    db_event = (
        db.query(models.InventoryEvent).filter(models.InventoryEvent.id == id).first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Inventory event not found")
    return db_event


@router.get("/events/", response_model=List[schemas.InventoryEventOut])
def list_inventory_events(db: Session = Depends(get_db)) -> List[models.InventoryEvent]:
    """List all inventory events."""
    return db.query(models.InventoryEvent).all()


# ----------------------
# LEGACY ENDPOINTS (Spanish names for backwards compatibility)
# ----------------------


# Inventory legacy endpoints
@router.post("/inventario/", response_model=schemas.InventoryOut)
def crear_inventario(
    inventario: schemas.InventoryCreate, db: Session = Depends(get_db)
) -> models.Inventory:
    """Legacy: Create inventory (Spanish name)."""
    return create_inventory(inventario, db)


@router.get("/inventario/{id}", response_model=schemas.InventoryOut)
def obtener_inventario(id: int, db: Session = Depends(get_db)) -> models.Inventory:
    """Legacy: Get inventory (Spanish name)."""
    return get_inventory(id, db)


@router.get("/inventarios/", response_model=List[schemas.InventoryOut])
def listar_inventarios(db: Session = Depends(get_db)) -> List[models.Inventory]:
    """Legacy: List inventories (Spanish name)."""
    return list_inventories(db)


# Event legacy endpoints
@router.post("/evento/", response_model=schemas.InventoryEventOut)
def crear_evento_inventario(
    evento: schemas.InventoryEventCreate, db: Session = Depends(get_db)
) -> models.InventoryEvent:
    """Legacy: Create inventory event (Spanish name)."""
    return create_inventory_event(evento, db)


@router.get("/evento/{id}", response_model=schemas.InventoryEventOut)
def obtener_evento(id: int, db: Session = Depends(get_db)) -> models.InventoryEvent:
    """Legacy: Get inventory event (Spanish name)."""
    return get_inventory_event(id, db)


@router.get("/eventos/", response_model=List[schemas.InventoryEventOut])
def listar_eventos(db: Session = Depends(get_db)) -> List[models.InventoryEvent]:
    """Legacy: List inventory events (Spanish name)."""
    return list_inventory_events(db)
