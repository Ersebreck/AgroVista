from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    activities,
    chat,
    control,
    economy,
    inventory,
    locations,
    parcels,
    simulation,
    terrains,
)

# Create FastAPI application
app = FastAPI(
    title="AgroVista API",
    description="Agricultural land management platform API",
    version="1.0.0",
)

# CORS middleware for development (adjust allow_origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Specify ["http://localhost:8501"] to only allow local Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route modules
app.include_router(terrains.router)
app.include_router(parcels.router)
app.include_router(locations.router)
app.include_router(activities.router)
app.include_router(chat.router)
app.include_router(economy.router)
app.include_router(inventory.router)
app.include_router(simulation.router)
app.include_router(control.router)


@app.get("/")
def read_root() -> Dict[str, str]:
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to AgroVista API. Use the endpoints to interact with agricultural data.",
        "docs": "Visit /docs for interactive API documentation",
    }
