import os

from sqlalchemy import (
    JSON,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

# Conditional imports for geo types
TESTING = os.getenv("TESTING", "False").lower() == "true"
if not TESTING:
    try:
        from geoalchemy2 import Geometry

        GEOMETRY_TYPE = Geometry(geometry_type="GEOMETRY", srid=4326)
        JSON_TYPE = JSONB
    except ImportError:
        # Fallback for environments without PostGIS
        GEOMETRY_TYPE = Text
        JSON_TYPE = JSON
else:
    # Use Text and JSON for testing with SQLite
    GEOMETRY_TYPE = Text
    JSON_TYPE = JSON

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # User full name
    email = Column(String, unique=True, nullable=False)  # Email address
    password = Column(String, nullable=False)  # Password (should be hashed)
    role = Column(String, nullable=False)  # Role: "owner", "manager", "admin"

    # Relationships
    activities = relationship("Activity", back_populates="user")
    simulations = relationship(
        "Simulation", backref="user", cascade="all, delete-orphan"
    )
    changes = relationship(
        "ChangeHistory", backref="user", cascade="all, delete-orphan"
    )


class Terrain(Base):
    """Terrain model representing large land areas containing multiple parcels."""

    __tablename__ = "terrains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Terrain name
    description = Column(Text)  # Optional description
    owner_id = Column(Integer, ForeignKey("users.id"))  # Owner reference
    location_id = Column(Integer, ForeignKey("locations.id"))  # Location reference

    # Relationships
    owner = relationship("User")
    parcels = relationship("Parcel", back_populates="terrain")


class Parcel(Base):
    """Parcel model representing individual land units for specific agricultural activities."""

    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Parcel name
    current_use = Column(String)  # Current use: "corn", "pasture", "greenhouse", etc.
    status = Column(String)  # Status: "active", "maintenance", "fallow"
    terrain_id = Column(Integer, ForeignKey("terrains.id"))  # Parent terrain
    location_id = Column(Integer, ForeignKey("locations.id"))  # Geographic location

    # Relationships
    terrain = relationship("Terrain", back_populates="parcels")
    activities = relationship("Activity", back_populates="parcel")
    inventories = relationship(
        "Inventory", backref="parcel", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", backref="parcel", cascade="all, delete-orphan"
    )
    budgets = relationship("Budget", backref="parcel", cascade="all, delete-orphan")
    indicators = relationship(
        "Indicator", backref="parcel", cascade="all, delete-orphan"
    )
    biological_parameters = relationship(
        "BiologicalParameter", backref="parcel", cascade="all, delete-orphan"
    )


class Activity(Base):
    """Activity model for tracking agricultural operations performed on parcels."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    type = Column(
        String, nullable=False
    )  # Activity type: "Fertilization", "Harvest", "Weighing", "Irrigation"
    date = Column(Date, nullable=False)  # Date when activity was performed
    description = Column(Text)  # Optional detailed description
    user_id = Column(Integer, ForeignKey("users.id"))  # User who performed the activity
    parcel_id = Column(Integer, ForeignKey("parcels.id"))  # Target parcel

    # Relationships
    user = relationship("User", back_populates="activities")
    parcel = relationship("Parcel", back_populates="activities")
    details = relationship(
        "ActivityDetail", back_populates="activity", cascade="all, delete-orphan"
    )
    inventory_events = relationship(
        "InventoryEvent", backref="activity", cascade="all, delete-orphan"
    )


class ActivityDetail(Base):
    """Activity detail model for storing specific measurements and data from activities."""

    __tablename__ = "activity_details"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    name = Column(
        String, nullable=False
    )  # Measurement name: "Water used", "Kg harvested"
    value = Column(String, nullable=False)  # Value: "800", "300"
    unit = Column(String, nullable=True)  # Unit: "l", "kg"

    # Relationships
    activity = relationship("Activity", back_populates="details")


class Location(Base):
    """Location model for storing geographic coordinates using PostGIS."""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Type: "point", "polygon"
    coordinates = Column(GEOMETRY_TYPE)  # PostGIS Geometry or Text for testing
    reference = Column(JSON_TYPE, nullable=True)  # Additional reference data

    # Relationships
    terrains = relationship("Terrain", backref="location")
    parcels = relationship("Parcel", backref="location")


# -------------------------
# INVENTORY AND MOVEMENT
# -------------------------


class Inventory(Base):
    """Inventory model for tracking supplies and materials."""

    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Item name: "NPK fertilizer", "Pesticide 1"
    type = Column(String, nullable=False)  # Type: "fertilizer", "pesticide", "vaccine"
    current_quantity = Column(Float, nullable=False)  # Current quantity available
    unit = Column(String, nullable=False)  # Unit: "kg", "l", "dose"
    parcel_id = Column(
        Integer, ForeignKey("parcels.id"), nullable=True
    )  # Associated parcel

    # Relationships
    movements = relationship("InventoryEvent", back_populates="inventory")


class InventoryEvent(Base):
    """Inventory event model for tracking inventory movements (in/out)."""

    __tablename__ = "inventory_events"

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"))
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=True
    )  # Optional activity link
    movement_type = Column(
        String, nullable=False
    )  # Movement type: "inbound", "outbound", "adjustment"
    quantity = Column(Float, nullable=False)  # Quantity moved
    date = Column(Date, nullable=False)  # Date of movement
    observation = Column(Text, nullable=True)  # Optional observation

    # Relationships
    inventory = relationship("Inventory", back_populates="movements")


# -------------------------
# ECONOMY AND BUDGET
# -------------------------


class Transaction(Base):
    """Transaction model for financial tracking (income and expenses)."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)  # Transaction date
    type = Column(String, nullable=False)  # Type: "expense" or "income"
    category = Column(
        String, nullable=False
    )  # Category: "fertilizer purchase", "milk sales"
    description = Column(Text)  # Optional description
    amount = Column(Float, nullable=False)  # Amount
    parcel_id = Column(Integer, ForeignKey("parcels.id"))  # Associated parcel
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=True
    )  # Related activity


class Budget(Base):
    """Budget model for planning yearly expenses by category."""

    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)  # Budget year
    category = Column(String, nullable=False)  # Expense category
    estimated_amount = Column(Float, nullable=False)  # Estimated amount
    parcel_id = Column(Integer, ForeignKey("parcels.id"))  # Associated parcel


# -------------------------
# PARAMETERS AND SIMULATIONS
# -------------------------


class BiologicalParameter(Base):
    """Biological parameter model for storing growth rates and biological data."""

    __tablename__ = "biological_parameters"

    id = Column(Integer, primary_key=True)
    name = Column(
        String, nullable=False
    )  # Parameter name: "livestock growth", "crop cycle"
    value = Column(Float, nullable=False)  # Parameter value
    unit = Column(String, nullable=True)  # Unit: "kg/month", "days"
    description = Column(Text)  # Description
    parcel_id = Column(Integer, ForeignKey("parcels.id"))  # Associated parcel


class Simulation(Base):
    """Simulation model for storing projection scenarios and results."""

    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Simulation name
    description = Column(Text)  # Description
    creation_date = Column(Date, nullable=False)  # Creation date
    parameters = Column(JSON_TYPE, nullable=True)  # Input parameters (JSON)
    results = Column(JSON_TYPE, nullable=True)  # Simulation results (JSON)
    user_id = Column(Integer, ForeignKey("users.id"))  # Creator user


# -------------------------
# TRACEABILITY AND KPIs
# -------------------------


class ChangeHistory(Base):
    """Change history model for auditing data modifications."""

    __tablename__ = "change_history"

    id = Column(Integer, primary_key=True)
    table = Column(String, nullable=False)  # Table name that was modified
    field = Column(String, nullable=False)  # Field name that was modified
    previous_value = Column(String, nullable=True)  # Previous value
    new_value = Column(String, nullable=True)  # New value
    date = Column(Date, nullable=False)  # Change date
    user_id = Column(Integer, ForeignKey("users.id"))  # User who made the change
    reason = Column(Text)  # Reason for the change


class Indicator(Base):
    """Indicator model for storing KPIs and performance metrics."""

    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Indicator name
    value = Column(Float, nullable=False)  # Indicator value
    unit = Column(String, nullable=True)  # Unit of measurement
    date = Column(Date, nullable=False)  # Measurement date
    parcel_id = Column(Integer, ForeignKey("parcels.id"))  # Associated parcel
    description = Column(Text)  # Description
