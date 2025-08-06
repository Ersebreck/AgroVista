"""
Terrain API routes v1.
Thin controllers that delegate to services.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.terrain_service import TerrainService
from app.core.dependencies import ServiceDependencies, get_skip_limit
from app.core.exceptions import (
    DomainException,
    TerrainNotFoundException,
    domain_exception_to_http,
)
from app.domain.farming.schemas import (
    Terrain,
    TerrainCreate,
    TerrainSummary,
    TerrainUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/terrains",
    tags=["terrains"],
    responses={
        404: {"description": "Terrain not found"},
        403: {"description": "Not authorized"},
    },
)


@router.post("/", response_model=Terrain, status_code=status.HTTP_201_CREATED)
async def create_terrain(
    terrain_data: TerrainCreate,
    terrain_service: TerrainService = Depends(ServiceDependencies.get_terrain_service),
    current_user_id: int = 1,  # TODO: Replace with actual auth dependency
) -> Terrain:
    """
    Create a new terrain.

    - **name**: Terrain name (required)
    - **description**: Optional description
    - **owner_id**: ID of the owner (must match current user)
    - **location_id**: Optional location reference
    """
    try:
        return terrain_service.create_terrain(terrain_data, current_user_id)
    except DomainException as e:
        logger.error(f"Domain error creating terrain: {e}")
        raise domain_exception_to_http(e)
    except Exception as e:
        logger.error(f"Unexpected error creating terrain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/{terrain_id}", response_model=Dict[str, Any])
async def get_terrain(
    terrain_id: int,
    terrain_service: TerrainService = Depends(ServiceDependencies.get_terrain_service),
    current_user_id: int = 1,  # TODO: Replace with actual auth dependency
) -> Dict[str, Any]:
    """
    Get terrain by ID with statistics.

    Returns terrain data along with:
    - Total number of parcels
    - Number of active parcels
    - Number of inactive parcels
    """
    try:
        return terrain_service.get_terrain(terrain_id, current_user_id)
    except TerrainNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Terrain with ID {terrain_id} not found",
        )
    except DomainException as e:
        raise domain_exception_to_http(e)


@router.get("/", response_model=List[TerrainSummary])
async def list_terrains(
    pagination: dict = Depends(get_skip_limit),
    search: Optional[str] = Query(None, description="Search by name"),
    terrain_service: TerrainService = Depends(ServiceDependencies.get_terrain_service),
    current_user_id: int = 1,  # TODO: Replace with actual auth dependency
) -> List[TerrainSummary]:
    """
    List terrains for the current user.

    - **skip**: Number of terrains to skip (pagination)
    - **limit**: Maximum number of terrains to return
    - **search**: Optional search by terrain name
    """
    if search:
        return terrain_service.search_terrains(search, current_user_id)

    return terrain_service.list_user_terrains(
        current_user_id, skip=pagination["skip"], limit=pagination["limit"]
    )


@router.put("/{terrain_id}", response_model=Terrain)
async def update_terrain(
    terrain_id: int,
    terrain_update: TerrainUpdate,
    terrain_service: TerrainService = Depends(ServiceDependencies.get_terrain_service),
    current_user_id: int = 1,  # TODO: Replace with actual auth dependency
) -> Terrain:
    """
    Update terrain information.

    All fields are optional - only provided fields will be updated.
    """
    try:
        return terrain_service.update_terrain(
            terrain_id, terrain_update, current_user_id
        )
    except DomainException as e:
        raise domain_exception_to_http(e)


@router.delete("/{terrain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terrain(
    terrain_id: int,
    terrain_service: TerrainService = Depends(ServiceDependencies.get_terrain_service),
    current_user_id: int = 1,  # TODO: Replace with actual auth dependency
) -> None:
    """
    Delete a terrain.

    Note: Terrain must not have any parcels to be deleted.
    """
    try:
        terrain_service.delete_terrain(terrain_id, current_user_id)
    except DomainException as e:
        raise domain_exception_to_http(e)
