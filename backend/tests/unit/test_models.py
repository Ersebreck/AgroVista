"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from app.models import (
    User, Terrain, Parcel, Activity, ActivityDetail,
    Location, Inventory, InventoryEvent, Transaction,
    Budget, BiologicalParameter, Simulation, ChangeHistory, Indicator
)


class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            name="Test User",
            password="hashed_password",
            role="owner"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.role == "owner"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_user_unique_email(self, db_session):
        """Test email uniqueness constraint."""
        user1 = User(
            email="unique@example.com",
            name="User 1",
            password="password",
            role="owner"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same email
        user2 = User(
            email="unique@example.com",
            name="User 2",
            password="password",
            role="manager"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_user_relationships(self, db_session, sample_user):
        """Test user relationships."""
        # Create related objects
        terrain = Terrain(name="Test Terrain", owner_id=sample_user.id)
        db_session.add(terrain)
        
        # Note: Inventory model doesn't have a direct user relationship
        # Creating a simple inventory item
        parcel = Parcel(name="Test Parcel", terrain_id=terrain.id)
        db_session.add(parcel)
        db_session.flush()
        
        inventory = Inventory(
            name="Seeds",
            type="seeds",
            current_quantity=100,
            unit="kg",
            parcel_id=parcel.id
        )
        db_session.add(inventory)
        db_session.commit()
        
        # Test relationships
        activity = Activity(
            type="Planting",
            date=date.today(),
            description="Planting seeds",
            user_id=sample_user.id,
            parcel_id=parcel.id
        )
        db_session.add(activity)
        db_session.commit()
        
        assert len(sample_user.activities) == 1
        assert sample_user.activities[0].type == "Planting"


class TestTerrainModel:
    """Test Terrain model functionality."""
    
    def test_create_terrain(self, db_session, sample_user):
        """Test creating a terrain."""
        terrain = Terrain(
            name="My Farm",
            description="A beautiful farm",
            owner_id=sample_user.id
        )
        db_session.add(terrain)
        db_session.commit()
        
        assert terrain.id is not None
        assert terrain.name == "My Farm"
        assert terrain.owner_id == sample_user.id
    
    def test_terrain_relationships(self, db_session, sample_terrain):
        """Test terrain relationships."""
        # Create parcels
        parcel1 = Parcel(name="Parcel 1", terrain_id=sample_terrain.id)
        parcel2 = Parcel(name="Parcel 2", terrain_id=sample_terrain.id)
        db_session.add_all([parcel1, parcel2])
        db_session.commit()
        
        # Test relationships
        assert len(sample_terrain.parcels) == 2
        assert sample_terrain.parcels[0].name == "Parcel 1"
        assert sample_terrain.parcels[1].name == "Parcel 2"
        assert sample_terrain.owner.name == "Test User"


class TestParcelModel:
    """Test Parcel model functionality."""
    
    def test_create_parcel(self, db_session, sample_terrain):
        """Test creating a parcel."""
        parcel = Parcel(
            name="North Field",
            current_use="corn",
            status="active",
            terrain_id=sample_terrain.id
        )
        db_session.add(parcel)
        db_session.commit()
        
        assert parcel.id is not None
        assert parcel.name == "North Field"
        assert parcel.terrain_id == sample_terrain.id
    
    def test_parcel_relationships(self, db_session, sample_parcel, sample_user):
        """Test parcel relationships."""
        # Create activities for the parcel
        activity1 = Activity(
            type="Planting",
            description="Plant seeds",
            user_id=sample_user.id,
            parcel_id=sample_parcel.id,
            date=date.today()
        )
        activity2 = Activity(
            type="Harvest",
            description="Harvest crops",
            user_id=sample_user.id,
            parcel_id=sample_parcel.id,
            date=date.today()
        )
        db_session.add_all([activity1, activity2])
        db_session.commit()
        
        # Test relationships
        assert len(sample_parcel.activities) == 2
        assert sample_parcel.terrain.name == "Test Farm"


class TestActivityModel:
    """Test Activity model functionality."""
    
    def test_create_activity(self, db_session, sample_user, sample_parcel):
        """Test creating an activity."""
        activity = Activity(
            type="Harvest",
            description="Harvest tomatoes",
            user_id=sample_user.id,
            parcel_id=sample_parcel.id,
            date=date(2024, 7, 1)
        )
        db_session.add(activity)
        db_session.commit()
        
        assert activity.id is not None
        assert activity.type == "Harvest"
        assert activity.description == "Harvest tomatoes"
        assert activity.date == date(2024, 7, 1)
    
    def test_activity_details(self, db_session, sample_activity):
        """Test activity details relationship."""
        # Create activity details
        detail1 = ActivityDetail(
            activity_id=sample_activity.id,
            name="Workers",
            value="5",
            unit="people"
        )
        detail2 = ActivityDetail(
            activity_id=sample_activity.id,
            name="Duration",
            value="8",
            unit="hours"
        )
        db_session.add_all([detail1, detail2])
        db_session.commit()
        
        # Test relationships
        assert len(sample_activity.details) == 2
        assert sample_activity.details[0].name == "Workers"
        assert sample_activity.details[1].name == "Duration"


class TestInventoryModel:
    """Test Inventory model functionality."""
    
    def test_create_inventory(self, db_session, sample_user):
        """Test creating inventory item."""
        inventory = Inventory(
            name="Fertilizer",
            type="fertilizer",
            unit="kg",
            current_quantity=500.0
        )
        db_session.add(inventory)
        db_session.commit()
        
        assert inventory.id is not None
        assert inventory.name == "Fertilizer"
        assert inventory.type == "fertilizer"
        assert inventory.current_quantity == 500.0
        assert inventory.unit == "kg"
    
    def test_inventory_events(self, db_session, sample_inventory):
        """Test inventory events."""
        from datetime import date
        # Create events
        event1 = InventoryEvent(
            inventory_id=sample_inventory.id,
            movement_type="inbound",
            quantity=50.0,
            date=date(2024, 1, 1),
            observation="Test entry"
        )
        event2 = InventoryEvent(
            inventory_id=sample_inventory.id,
            movement_type="outbound",
            quantity=20.0,
            date=date(2024, 1, 2),
            observation="Test exit"
        )
        db_session.add_all([event1, event2])
        db_session.commit()
        
        # Test relationships
        assert len(sample_inventory.movements) == 2
        assert sample_inventory.movements[0].quantity == 50.0
        assert sample_inventory.movements[1].quantity == 20.0


class TestTransactionModel:
    """Test Transaction model functionality."""
    
    def test_create_transaction(self, db_session, sample_parcel, sample_activity):
        """Test creating a transaction."""
        from datetime import date
        transaction = Transaction(
            type="expense",
            category="purchases",
            amount=250.50,
            date=date(2024, 7, 1),
            description="Tomato seeds",
            parcel_id=sample_parcel.id,
            activity_id=sample_activity.id
        )
        db_session.add(transaction)
        db_session.commit()
        
        assert transaction.id is not None
        assert transaction.type == "expense"
        assert transaction.category == "purchases"
        assert transaction.amount == 250.50
        assert transaction.date == date(2024, 7, 1)
    
    def test_transaction_relationships(self, db_session, sample_parcel, sample_activity):
        """Test transaction relationships."""
        from datetime import date
        transaction = Transaction(
            type="expense",
            category="labor",
            amount=500.0,
            date=date(2024, 7, 1),
            parcel_id=sample_parcel.id,
            activity_id=sample_activity.id
        )
        db_session.add(transaction)
        db_session.commit()
        
        assert transaction.parcel_id == sample_parcel.id
        assert transaction.activity_id == sample_activity.id


class TestBudgetModel:
    """Test Budget model functionality."""
    
    def test_create_budget(self, db_session, sample_parcel):
        """Test creating a budget."""
        budget = Budget(
            year=2024,
            category="operations",
            estimated_amount=10000.0,
            parcel_id=sample_parcel.id
        )
        db_session.add(budget)
        db_session.commit()
        
        assert budget.id is not None
        assert budget.year == 2024
        assert budget.category == "operations"
        assert budget.estimated_amount == 10000.0
        assert budget.parcel_id == sample_parcel.id


class TestBiologicalParameterModel:
    """Test BiologicalParameter model functionality."""
    
    def test_create_biological_parameter(self, db_session, sample_parcel):
        """Test creating a biological parameter."""
        param = BiologicalParameter(
            name="Soil pH",
            value=6.5,
            unit="pH",
            description="Soil acidity measurement",
            parcel_id=sample_parcel.id
        )
        db_session.add(param)
        db_session.commit()
        
        assert param.id is not None
        assert param.name == "Soil pH"
        assert param.value == 6.5
        assert param.unit == "pH"
        assert param.description == "Soil acidity measurement"


class TestSimulationModel:
    """Test Simulation model functionality."""
    
    def test_create_simulation(self, db_session, sample_user):
        """Test creating a simulation."""
        from datetime import date
        simulation = Simulation(
            name="Crop Yield Simulation",
            description="Simulating tomato yield",
            creation_date=date(2024, 1, 1),
            user_id=sample_user.id,
            parameters={"temperature": 25, "humidity": 70},
            results={"yield": 5000, "quality": "high"}
        )
        db_session.add(simulation)
        db_session.commit()
        
        assert simulation.id is not None
        assert simulation.name == "Crop Yield Simulation"
        assert simulation.parameters["temperature"] == 25
        assert simulation.results["yield"] == 5000
        assert simulation.creation_date == date(2024, 1, 1)
