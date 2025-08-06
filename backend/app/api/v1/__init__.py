"""
API v1 main router.
Aggregates all v1 route modules.
"""

from fastapi import APIRouter

from app.api.v1.routes import terrains

# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include route modules
api_router.include_router(terrains.router)

# Future route modules will be added here:
# api_router.include_router(parcels.router)
# api_router.include_router(activities.router)
# api_router.include_router(inventory.router)
# api_router.include_router(finance.router)
# api_router.include_router(simulation.router)
