"""
Global test configuration and fixtures.
"""
import os
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator

# Set testing environment
os.environ["TESTING"] = "True"

from app.main import app as fastapi_app
from app.db import get_db
import app.models  # Import all models to register them
from app.models import Base, User, Terrain, Parcel, Activity, Location, Inventory


# Test database configuration - using in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Configure SQLite engine with proper settings for testing
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator:
    """Create a test client with overridden database."""
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(fastapi_app) as test_client:
        yield test_client
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        name="Test User",
        password="hashed_test_password",
        role="owner"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_terrain(db_session: Session, sample_user: User) -> Terrain:
    """Create a sample terrain for testing."""
    terrain = Terrain(
        name="Test Farm",
        description="A test farm for unit testing",
        owner_id=sample_user.id,
        location_id=None
    )
    db_session.add(terrain)
    db_session.commit()
    db_session.refresh(terrain)
    return terrain


@pytest.fixture
def sample_parcel(db_session: Session, sample_terrain: Terrain) -> Parcel:
    """Create a sample parcel for testing."""
    parcel = Parcel(
        name="Test Parcel",
        current_use="wheat",
        status="active",
        terrain_id=sample_terrain.id,
        location_id=None
    )
    db_session.add(parcel)
    db_session.commit()
    db_session.refresh(parcel)
    return parcel


@pytest.fixture
def sample_location(db_session: Session) -> Location:
    """Create a sample location for testing."""
    location = Location(
        type="point",
        coordinates=None,  # Simplified for testing
        reference={"test": "location"}
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_activity(db_session: Session, sample_user: User, sample_parcel: Parcel) -> Activity:
    """Create a sample activity for testing."""
    from datetime import date
    activity = Activity(
        type="Maintenance",
        description="A test activity",
        user_id=sample_user.id,
        parcel_id=sample_parcel.id,
        date=date(2024, 1, 1)
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity


@pytest.fixture
def sample_inventory(db_session: Session) -> Inventory:
    """Create a sample inventory item for testing."""
    inventory = Inventory(
        name="Test Item",
        type="supplies",
        unit="kg",
        current_quantity=100.0
    )
    db_session.add(inventory)
    db_session.commit()
    db_session.refresh(inventory)
    return inventory
