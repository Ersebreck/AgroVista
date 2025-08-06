"""
Farming domain schemas.
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# Base schemas
class LocationBase(BaseModel):
    """Base schema for location data."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(default="point", regex="^(point|polygon|linestring)$")
    coordinates: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TerrainBase(BaseModel):
    """Base schema for terrain data."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ParcelBase(BaseModel):
    """Base schema for parcel data."""

    name: str = Field(..., min_length=1, max_length=100)
    current_use: Optional[str] = Field(None, max_length=50)
    status: str = Field(default="active", regex="^(active|maintenance|fallow)$")

    @validator("status")
    def validate_status(cls, v):
        allowed_statuses = ["active", "maintenance", "fallow"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


# Create schemas
class LocationCreate(LocationBase):
    """Schema for creating a location."""

    parcel_id: Optional[int] = None


class TerrainCreate(TerrainBase):
    """Schema for creating a terrain."""

    owner_id: int
    location_id: Optional[int] = None


class ParcelCreate(ParcelBase):
    """Schema for creating a parcel."""

    terrain_id: int
    location_id: Optional[int] = None


# Update schemas
class LocationUpdate(BaseModel):
    """Schema for updating a location."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = Field(None, regex="^(point|polygon|linestring)$")
    coordinates: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TerrainUpdate(BaseModel):
    """Schema for updating a terrain."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location_id: Optional[int] = None


class ParcelUpdate(BaseModel):
    """Schema for updating a parcel."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    current_use: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, regex="^(active|maintenance|fallow)$")
    location_id: Optional[int] = None


# Response schemas
class Location(LocationBase):
    """Schema for location responses."""

    id: int
    parcel_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TerrainSummary(BaseModel):
    """Summary schema for terrain in lists."""

    id: int
    name: str
    description: Optional[str]
    parcel_count: int = 0

    class Config:
        orm_mode = True


class Terrain(TerrainBase):
    """Schema for terrain responses."""

    id: int
    owner_id: int
    location_id: Optional[int]
    location: Optional[Location] = None
    parcels: List["ParcelSummary"] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ParcelSummary(BaseModel):
    """Summary schema for parcel in lists."""

    id: int
    name: str
    current_use: Optional[str]
    status: str

    class Config:
        orm_mode = True


class Parcel(ParcelBase):
    """Schema for parcel responses."""

    id: int
    terrain_id: int
    location_id: Optional[int]
    location: Optional[Location] = None
    terrain_name: Optional[str] = None
    activity_count: int = 0
    last_activity_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Update forward references
Terrain.update_forward_refs()
Parcel.update_forward_refs()
