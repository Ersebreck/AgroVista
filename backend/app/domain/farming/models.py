"""
Farming domain models.
Contains models related to terrains, parcels, and locations.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base


class Terrain(Base):
    """Terrain model representing large land areas containing multiple parcels."""

    __tablename__ = "terrains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    # Relationships
    owner = relationship("User", back_populates="terrains")
    parcels = relationship(
        "Parcel", back_populates="terrain", cascade="all, delete-orphan"
    )
    location = relationship(
        "Location", back_populates="terrains", foreign_keys=[location_id]
    )


class Parcel(Base):
    """Parcel model representing individual land units for specific agricultural activities."""

    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    current_use = Column(String)  # Current use: "corn", "pasture", "greenhouse", etc.
    status = Column(String)  # Status: "active", "maintenance", "fallow"
    terrain_id = Column(Integer, ForeignKey("terrains.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    # Relationships
    terrain = relationship("Terrain", back_populates="parcels")
    location = relationship(
        "Location", back_populates="parcels", foreign_keys=[location_id]
    )
    activities = relationship(
        "Activity", back_populates="parcel", cascade="all, delete-orphan"
    )
    inventories = relationship(
        "Inventory", back_populates="parcel", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="parcel", cascade="all, delete-orphan"
    )
    budgets = relationship(
        "Budget", back_populates="parcel", cascade="all, delete-orphan"
    )
    indicators = relationship(
        "Indicator", back_populates="parcel", cascade="all, delete-orphan"
    )
    biological_parameters = relationship(
        "BiologicalParameter", back_populates="parcel", cascade="all, delete-orphan"
    )


class Location(Base):
    """Location model for storing geographic coordinates using PostGIS."""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=True)
    type = Column(String, nullable=False, default="point")  # point, polygon, etc.
    coordinates = Column(Geometry(geometry_type="GEOMETRY", srid=4326))
    metadata = Column(JSONB, nullable=True)  # Additional location metadata

    # Relationships
    terrains = relationship(
        "Terrain", back_populates="location", foreign_keys="[Terrain.location_id]"
    )
    parcels = relationship(
        "Parcel", back_populates="location", foreign_keys="[Parcel.location_id]"
    )
