"""
Terrain repository implementation.
Handles data access for terrain entities.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.repositories.base import BaseRepository
from app.models import Parcel, Terrain


class TerrainRepository(BaseRepository[Terrain]):
    """Repository for terrain data access."""

    def __init__(self, db: Session):
        super().__init__(Terrain, db)

    def get_with_parcels(self, terrain_id: int) -> Optional[Terrain]:
        """
        Get terrain with its parcels loaded.

        Args:
            terrain_id: ID of the terrain

        Returns:
            Terrain with parcels or None
        """
        return (
            self.db.query(Terrain)
            .options(joinedload(Terrain.parcels))
            .filter(Terrain.id == terrain_id)
            .first()
        )

    def get_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Terrain]:
        """
        Get all terrains owned by a user.

        Args:
            owner_id: ID of the owner
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of terrains
        """
        return (
            self.db.query(Terrain)
            .filter(Terrain.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_stats(self, terrain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get terrain with statistics.

        Args:
            terrain_id: ID of the terrain

        Returns:
            Dictionary with terrain data and stats
        """
        terrain = self.get(terrain_id)
        if not terrain:
            return None

        # Get parcel statistics
        parcel_stats = (
            self.db.query(
                func.count(Parcel.id).label("total_parcels"),
                func.count(
                    func.distinct(
                        func.case([(Parcel.status == "active", Parcel.id)], else_=None)
                    )
                ).label("active_parcels"),
            )
            .filter(Parcel.terrain_id == terrain_id)
            .first()
        )

        return {
            "terrain": terrain,
            "statistics": {
                "total_parcels": parcel_stats.total_parcels or 0,
                "active_parcels": parcel_stats.active_parcels or 0,
                "inactive_parcels": (parcel_stats.total_parcels or 0)
                - (parcel_stats.active_parcels or 0),
            },
        }

    def search_by_name(
        self, name: str, owner_id: Optional[int] = None
    ) -> List[Terrain]:
        """
        Search terrains by name.

        Args:
            name: Name pattern to search
            owner_id: Optional owner filter

        Returns:
            List of matching terrains
        """
        query = self.db.query(Terrain).filter(Terrain.name.ilike(f"%{name}%"))

        if owner_id:
            query = query.filter(Terrain.owner_id == owner_id)

        return query.all()

    def has_parcels(self, terrain_id: int) -> bool:
        """
        Check if terrain has any parcels.

        Args:
            terrain_id: ID of the terrain

        Returns:
            True if terrain has parcels
        """
        return self.db.query(
            self.db.query(Parcel).filter(Parcel.terrain_id == terrain_id).exists()
        ).scalar()

    def delete_with_validation(self, terrain_id: int) -> bool:
        """
        Delete terrain only if it has no parcels.

        Args:
            terrain_id: ID of the terrain

        Returns:
            True if deleted

        Raises:
            InvalidOperationException: If terrain has parcels
        """
        from app.core.exceptions import InvalidOperationException

        if self.has_parcels(terrain_id):
            raise InvalidOperationException(
                "Cannot delete terrain with existing parcels. Delete parcels first."
            )

        return self.delete(terrain_id)
