from datetime import date
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr

# ---------- USER ----------


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str  # Full name
    email: EmailStr  # Email address
    role: str  # Role: "owner", "manager", "admin"


class UserCreate(UserBase):
    """Schema for creating new users."""

    password: str  # Password (will be hashed)


class UserOut(UserBase):
    """Schema for user output (without password)."""

    id: int

    model_config = {"from_attributes": True}


# ---------- LOCATION ----------


class LocationBase(BaseModel):
    """Base location schema for geographic data."""

    type: str  # Type: "point" or "polygon"
    coordinates: dict  # Raw GeoJSON or use Point/Polygon for stricter validation
    reference: Optional[dict] = None  # Optional reference information


class LocationCreate(LocationBase):
    """Schema for creating new locations."""

    pass


class LocationOut(LocationBase):
    """Schema for location output."""

    id: int

    model_config = {"from_attributes": True}


# ---------- TERRAIN ----------


class TerrainBase(BaseModel):
    """Base terrain schema representing large land areas."""

    name: str  # Terrain name
    description: Optional[str] = None  # Optional description
    owner_id: int  # Owner user ID
    location_id: Optional[int] = None  # Location reference


class TerrainCreate(TerrainBase):
    """Schema for creating new terrains."""

    pass


class TerrainOut(TerrainBase):
    """Schema for terrain output."""

    id: int

    model_config = {"from_attributes": True}


# ---------- PARCEL ----------


class ParcelBase(BaseModel):
    """Base parcel schema for individual land units."""

    name: str  # Parcel name
    current_use: Optional[str] = None  # Current use: "corn", "pasture", "greenhouse"
    status: Optional[str] = None  # Status: "active", "maintenance", "fallow"
    terrain_id: int  # Parent terrain ID
    location_id: Optional[int] = None  # Location reference


class ParcelCreate(ParcelBase):
    """Schema for creating new parcels."""

    pass


class ParcelOut(ParcelBase):
    """Schema for parcel output."""

    id: int

    model_config = {"from_attributes": True}


# ---------- ACTIVITY ----------


class ActivityBase(BaseModel):
    """Base activity schema for agricultural operations."""

    type: str  # Activity type: "Fertilization", "Harvest", "Irrigation"
    date: date  # Date when activity was performed
    description: Optional[str] = None  # Optional detailed description
    user_id: int  # User who performed the activity
    parcel_id: int  # Target parcel ID


class ActivityCreate(ActivityBase):
    """Schema for creating new activities."""

    pass


class ActivityOut(ActivityBase):
    """Schema for activity output."""

    id: int

    model_config = {"from_attributes": True}


# ---------- ACTIVITY DETAIL ----------


class ActivityDetailCreate(BaseModel):
    """Schema for creating activity details."""

    activity_id: int  # Parent activity ID
    name: str  # Detail name: "Fertilizer", "Kg harvested", "Water used"
    value: str  # Value (can be number, text, or measurement)
    unit: Optional[str] = None  # Unit: "kg", "l", "m3"


class ActivityDetailOut(ActivityDetailCreate):
    """Schema for activity detail output."""

    id: int

    model_config = {"from_attributes": True}


# ---------- CHAT ----------


class ChatRequest(BaseModel):
    """Schema for chat requests to the agricultural assistant."""

    prompt: str  # User query or question


# ---------- INVENTORY AND INVENTORY EVENT ----------


class InventoryBase(BaseModel):
    """Base inventory schema for supplies and materials."""

    name: str  # Item name
    type: str  # Type: "Fertilizer", "Feed", "Machinery"
    current_quantity: float  # Current quantity
    unit: str  # Unit: "kg", "l", "units"
    parcel_id: Optional[int] = None  # Associated parcel ID


class InventoryCreate(InventoryBase):
    """Schema for creating new inventory items."""

    pass


class InventoryOut(InventoryBase):
    """Schema for inventory output."""

    id: int
    model_config = {"from_attributes": True}


class InventoryEventBase(BaseModel):
    """Base inventory event schema for tracking movements."""

    inventory_id: int  # Target inventory item ID
    activity_id: Optional[int] = None  # Related activity ID
    movement_type: str  # Movement type: "inbound" / "outbound"
    quantity: float  # Quantity moved
    date: date  # Movement date
    observation: Optional[str] = None  # Optional observation


class InventoryEventCreate(InventoryEventBase):
    """Schema for creating new inventory events."""

    pass


class InventoryEventOut(InventoryEventBase):
    """Schema for inventory event output."""

    id: int
    model_config = {"from_attributes": True}


# ---------- TRANSACTION AND BUDGET ----------


class TransactionBase(BaseModel):
    """Base transaction schema for financial tracking."""

    date: date  # Transaction date
    type: str  # Type: "income" / "expense"
    category: str  # Category: "fertilizer purchase", "milk sales"
    description: Optional[str]  # Optional description
    amount: float  # Amount
    parcel_id: int  # Associated parcel ID
    activity_id: Optional[int] = None  # Related activity ID


class TransactionCreate(TransactionBase):
    """Schema for creating new transactions."""

    pass


class TransactionOut(TransactionBase):
    """Schema for transaction output."""

    id: int
    model_config = {"from_attributes": True}


class BudgetBase(BaseModel):
    """Base budget schema for yearly expense planning."""

    year: int  # Budget year
    category: str  # Expense category
    estimated_amount: float  # Estimated amount
    parcel_id: int  # Associated parcel ID


class BudgetCreate(BudgetBase):
    """Schema for creating new budgets."""

    pass


class BudgetOut(BudgetBase):
    """Schema for budget output."""

    id: int
    model_config = {"from_attributes": True}


# ---------- BIOLOGICAL PARAMETERS AND SIMULATION ----------


class BiologicalParameterBase(BaseModel):
    """Base biological parameter schema for growth rates and biological data."""

    name: str  # Parameter name: "livestock growth", "crop cycle"
    value: float  # Parameter value
    unit: Optional[str] = None  # Unit: "kg/month", "days"
    description: Optional[str] = None  # Description
    parcel_id: int  # Associated parcel ID


class BiologicalParameterCreate(BiologicalParameterBase):
    """Schema for creating new biological parameters."""

    pass


class BiologicalParameterOut(BiologicalParameterBase):
    """Schema for biological parameter output."""

    id: int
    model_config = {"from_attributes": True}


class SimulationBase(BaseModel):
    """Base simulation schema for projection scenarios."""

    name: str  # Simulation name
    description: Optional[str]  # Description
    creation_date: date  # Creation date
    parameters: Optional[Dict[str, Any]] = None  # Input parameters (JSON)
    results: Optional[Dict[str, Any]] = None  # Simulation results (JSON)
    user_id: int  # Creator user ID


class SimulationCreate(SimulationBase):
    """Schema for creating new simulations."""

    pass


class SimulationOut(SimulationBase):
    """Schema for simulation output."""

    id: int
    model_config = {"from_attributes": True}


# ---------- CHANGE HISTORY AND KPI ----------


class ChangeHistoryBase(BaseModel):
    """Base change history schema for auditing data modifications."""

    table: str  # Table name that was modified
    field: str  # Field name that was modified
    previous_value: Optional[str]  # Previous value
    new_value: Optional[str]  # New value
    date: date  # Change date
    user_id: int  # User who made the change
    reason: Optional[str] = None  # Reason for the change


class ChangeHistoryCreate(ChangeHistoryBase):
    """Schema for creating new change history records."""

    pass


class ChangeHistoryOut(ChangeHistoryBase):
    """Schema for change history output."""

    id: int
    model_config = {"from_attributes": True}


class IndicatorBase(BaseModel):
    """Base indicator schema for KPIs and performance metrics."""

    name: str  # Indicator name
    value: float  # Indicator value
    unit: Optional[str] = None  # Unit of measurement
    date: date  # Measurement date
    parcel_id: int  # Associated parcel ID
    description: Optional[str] = None  # Description


class IndicatorCreate(IndicatorBase):
    """Schema for creating new indicators."""

    pass


class IndicatorOut(IndicatorBase):
    """Schema for indicator output."""

    id: int
    model_config = {"from_attributes": True}
