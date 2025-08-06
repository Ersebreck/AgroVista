"""
Dependency injection configuration.
Provides centralized dependency management for the application.
"""

import logging
from typing import Generator

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.application.services.terrain_service import TerrainService
from app.core.config import Settings, get_settings
from app.db import SessionLocal
from app.infrastructure.repositories.terrain_repository import TerrainRepository

# Logger instance
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Yields database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_settings() -> Settings:
    """Get current application settings."""
    return get_settings()


# Repository dependencies will be added here as we create them
class RepositoryDependencies:
    """Container for repository dependencies."""

    @staticmethod
    def get_terrain_repository(db: Session = Depends(get_db)):
        """Get terrain repository instance."""
        return TerrainRepository(db)

    @staticmethod
    def get_parcel_repository(db: Session = Depends(get_db)):
        """Get parcel repository instance."""
        from app.infrastructure.repositories.parcel_repository import ParcelRepository

        return ParcelRepository(db)

    @staticmethod
    def get_activity_repository(db: Session = Depends(get_db)):
        """Get activity repository instance."""
        from app.infrastructure.repositories.activity_repository import (
            ActivityRepository,
        )

        return ActivityRepository(db)

    @staticmethod
    def get_inventory_repository(db: Session = Depends(get_db)):
        """Get inventory repository instance."""
        from app.infrastructure.repositories.inventory_repository import (
            InventoryRepository,
        )

        return InventoryRepository(db)


# Service dependencies will be added here as we create them
class ServiceDependencies:
    """Container for service dependencies."""

    @staticmethod
    def get_terrain_service(
        terrain_repo=Depends(RepositoryDependencies.get_terrain_repository),
        settings: Settings = Depends(get_current_settings),
    ) -> TerrainService:
        """Get terrain service instance."""
        return TerrainService(terrain_repo, settings)

    @staticmethod
    def get_parcel_service(
        parcel_repo=Depends(RepositoryDependencies.get_parcel_repository),
        terrain_repo=Depends(RepositoryDependencies.get_terrain_repository),
        settings: Settings = Depends(get_current_settings),
    ):
        """Get parcel service instance."""
        from app.application.services.parcel_service import ParcelService

        return ParcelService(parcel_repo, terrain_repo, settings)


# Common dependencies


def get_skip_limit(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
) -> dict:
    """
    Common pagination parameters.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records (capped at 100)
    """
    return {"skip": skip, "limit": min(limit, 100)}
