"""
Terrain service implementation.
Contains business logic for terrain management.
"""

import logging
from typing import Any, Dict, List

from app.core.config import Settings
from app.core.exceptions import AuthorizationException, TerrainNotFoundException
from app.domain.farming.schemas import (
    Terrain,
    TerrainCreate,
    TerrainSummary,
    TerrainUpdate,
)
from app.infrastructure.repositories.terrain_repository import TerrainRepository

logger = logging.getLogger(__name__)


class TerrainService:
    """Service for terrain business operations."""

    def __init__(self, terrain_repository: TerrainRepository, settings: Settings):
        self.terrain_repo = terrain_repository
        self.settings = settings

    def create_terrain(self, terrain_data: TerrainCreate, user_id: int) -> Terrain:
        """
        Create a new terrain.

        Args:
            terrain_data: Terrain creation data
            user_id: ID of the user creating the terrain

        Returns:
            Created terrain
        """
        logger.info(f"Creating terrain '{terrain_data.name}' for user {user_id}")

        # Validate user owns the terrain
        if terrain_data.owner_id != user_id:
            raise AuthorizationException("create", "terrain for another user")

        # Create terrain
        terrain_dict = terrain_data.dict()
        db_terrain = self.terrain_repo.create(terrain_dict)

        logger.info(f"Terrain created with ID: {db_terrain.id}")
        return Terrain.from_orm(db_terrain)

    def get_terrain(self, terrain_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get terrain by ID with authorization check.

        Args:
            terrain_id: ID of the terrain
            user_id: ID of the requesting user

        Returns:
            Terrain with statistics

        Raises:
            TerrainNotFoundException: If terrain not found
            AuthorizationException: If user not authorized
        """
        terrain_data = self.terrain_repo.get_with_stats(terrain_id)

        if not terrain_data:
            raise TerrainNotFoundException(terrain_id)

        terrain = terrain_data["terrain"]

        # Check authorization
        if terrain.owner_id != user_id:
            raise AuthorizationException("view", "terrain")

        return {
            "terrain": Terrain.from_orm(terrain),
            "statistics": terrain_data["statistics"],
        }

    def list_user_terrains(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[TerrainSummary]:
        """
        List all terrains owned by a user.

        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of terrain summaries
        """
        terrains = self.terrain_repo.get_by_owner(user_id, skip, limit)

        # Convert to summary format with parcel count
        summaries = []
        for terrain in terrains:
            summary = TerrainSummary(
                id=terrain.id,
                name=terrain.name,
                description=terrain.description,
                parcel_count=len(terrain.parcels) if terrain.parcels else 0,
            )
            summaries.append(summary)

        return summaries

    def update_terrain(
        self, terrain_id: int, terrain_update: TerrainUpdate, user_id: int
    ) -> Terrain:
        """
        Update terrain information.

        Args:
            terrain_id: ID of the terrain
            terrain_update: Update data
            user_id: ID of the requesting user

        Returns:
            Updated terrain

        Raises:
            TerrainNotFoundException: If terrain not found
            AuthorizationException: If user not authorized
        """
        # Get existing terrain
        db_terrain = self.terrain_repo.get(terrain_id)
        if not db_terrain:
            raise TerrainNotFoundException(terrain_id)

        # Check authorization
        if db_terrain.owner_id != user_id:
            raise AuthorizationException("update", "terrain")

        # Update only provided fields
        update_data = terrain_update.dict(exclude_unset=True)
        if update_data:
            updated_terrain = self.terrain_repo.update(terrain_id, update_data)
            logger.info(f"Terrain {terrain_id} updated")
            return Terrain.from_orm(updated_terrain)

        return Terrain.from_orm(db_terrain)

    def delete_terrain(self, terrain_id: int, user_id: int) -> bool:
        """
        Delete a terrain.

        Args:
            terrain_id: ID of the terrain
            user_id: ID of the requesting user

        Returns:
            True if deleted

        Raises:
            TerrainNotFoundException: If terrain not found
            AuthorizationException: If user not authorized
            InvalidOperationException: If terrain has parcels
        """
        # Get existing terrain
        db_terrain = self.terrain_repo.get(terrain_id)
        if not db_terrain:
            raise TerrainNotFoundException(terrain_id)

        # Check authorization
        if db_terrain.owner_id != user_id:
            raise AuthorizationException("delete", "terrain")

        # Delete with validation (checks for parcels)
        result = self.terrain_repo.delete_with_validation(terrain_id)

        if result:
            logger.info(f"Terrain {terrain_id} deleted by user {user_id}")

        return result

    def search_terrains(self, name: str, user_id: int) -> List[TerrainSummary]:
        """
        Search terrains by name for a specific user.

        Args:
            name: Name pattern to search
            user_id: ID of the user

        Returns:
            List of matching terrain summaries
        """
        terrains = self.terrain_repo.search_by_name(name, user_id)

        return [
            TerrainSummary(
                id=t.id,
                name=t.name,
                description=t.description,
                parcel_count=len(t.parcels) if t.parcels else 0,
            )
            for t in terrains
        ]
