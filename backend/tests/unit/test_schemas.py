"""
Unit tests for Pydantic schemas.
"""
import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas import (
    UserCreate, UserOut,
    TerrainCreate, TerrainOut,
    ParcelCreate, ParcelOut,
    ActivityCreate, ActivityOut,
    ActivityDetailCreate, ActivityDetailOut,
    InventoryCreate, InventoryOut,
    InventoryEventCreate, InventoryEventOut,
    TransactionCreate, TransactionOut,
    BudgetCreate, BudgetOut,
    BiologicalParameterCreate, BiologicalParameterOut,
    SimulationCreate, SimulationOut,
    ChangeHistoryCreate, ChangeHistoryOut,
    IndicatorCreate, IndicatorOut,
    ChatRequest
)


class TestUserSchemas:
    """Test User-related schemas."""
    
    def test_user_create_valid(self):
        """Test creating a valid UserCreate schema."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "owner",
            "password": "securepassword123"
        }
        user = UserCreate(**user_data)
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == "owner"
        assert user.password == "securepassword123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        user_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "role": "owner",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_user_out_schema(self):
        """Test UserOut schema."""
        user_out_data = {
            "id": 1,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "role": "manager"
        }
        user_out = UserOut(**user_out_data)
        
        assert user_out.id == 1
        assert user_out.name == "Jane Doe"
        assert not hasattr(user_out, "password")


class TestTerrainSchemas:
    """Test Terrain-related schemas."""
    
    def test_terrain_create_valid(self):
        """Test creating a valid TerrainCreate schema."""
        terrain_data = {
            "name": "North Farm",
            "description": "Large agricultural land",
            "owner_id": 1,
            "location_id": None
        }
        terrain = TerrainCreate(**terrain_data)
        
        assert terrain.name == "North Farm"
        assert terrain.description == "Large agricultural land"
        assert terrain.owner_id == 1
        assert terrain.location_id is None
    
    def test_terrain_create_minimal(self):
        """Test creating TerrainCreate with minimal data."""
        terrain_data = {
            "name": "Small Farm",
            "owner_id": 2
        }
        terrain = TerrainCreate(**terrain_data)
        
        assert terrain.name == "Small Farm"
        assert terrain.owner_id == 2
        assert terrain.description is None
        assert terrain.location_id is None
    
    def test_terrain_out_schema(self):
        """Test TerrainOut schema."""
        terrain_out_data = {
            "id": 10,
            "name": "East Farm",
            "owner_id": 3,
            "description": "Fertile land",
            "location_id": 5
        }
        terrain_out = TerrainOut(**terrain_out_data)
        
        assert terrain_out.id == 10
        assert terrain_out.name == "East Farm"


class TestParcelSchemas:
    """Test Parcel-related schemas."""
    
    def test_parcel_create_valid(self):
        """Test creating a valid ParcelCreate schema."""
        parcel_data = {
            "name": "Field A",
            "current_use": "corn",
            "status": "active",
            "terrain_id": 1,
            "location_id": 2
        }
        parcel = ParcelCreate(**parcel_data)
        
        assert parcel.name == "Field A"
        assert parcel.current_use == "corn"
        assert parcel.status == "active"
        assert parcel.terrain_id == 1
    
    def test_parcel_create_minimal(self):
        """Test creating ParcelCreate with minimal data."""
        parcel_data = {
            "name": "Field B",
            "terrain_id": 1
        }
        parcel = ParcelCreate(**parcel_data)
        
        assert parcel.name == "Field B"
        assert parcel.terrain_id == 1
        assert parcel.current_use is None
        assert parcel.status is None


class TestActivitySchemas:
    """Test Activity-related schemas."""
    
    def test_activity_create_valid(self):
        """Test creating a valid ActivityCreate schema."""
        activity_data = {
            "type": "Fertilization",
            "date": date(2024, 7, 1),
            "description": "Applied NPK fertilizer",
            "user_id": 1,
            "parcel_id": 5
        }
        activity = ActivityCreate(**activity_data)
        
        assert activity.type == "Fertilization"
        assert activity.date == date(2024, 7, 1)
        assert activity.description == "Applied NPK fertilizer"
    
    def test_activity_detail_create(self):
        """Test creating ActivityDetailCreate schema."""
        detail_data = {
            "activity_id": 1,
            "name": "Fertilizer",
            "value": "50",
            "unit": "kg"
        }
        detail = ActivityDetailCreate(**detail_data)
        
        assert detail.activity_id == 1
        assert detail.name == "Fertilizer"
        assert detail.value == "50"
        assert detail.unit == "kg"


class TestInventorySchemas:
    """Test Inventory-related schemas."""
    
    def test_inventory_create_valid(self):
        """Test creating a valid InventoryCreate schema."""
        inventory_data = {
            "name": "NPK Fertilizer",
            "type": "Fertilizer",
            "current_quantity": 500.0,
            "unit": "kg",
            "parcel_id": 3
        }
        inventory = InventoryCreate(**inventory_data)
        
        assert inventory.name == "NPK Fertilizer"
        assert inventory.type == "Fertilizer"
        assert inventory.current_quantity == 500.0
    
    def test_inventory_event_create(self):
        """Test creating InventoryEventCreate schema."""
        event_data = {
            "inventory_id": 1,
            "activity_id": 2,
            "movement_type": "entry",
            "quantity": 100.0,
            "date": date(2024, 7, 1),
            "observation": "Purchase from supplier"
        }
        event = InventoryEventCreate(**event_data)
        
        assert event.inventory_id == 1
        assert event.movement_type == "entry"
        assert event.quantity == 100.0


class TestTransactionSchemas:
    """Test Transaction-related schemas."""
    
    def test_transaction_create_valid(self):
        """Test creating a valid TransactionCreate schema."""
        transaction_data = {
            "date": date(2024, 7, 1),
            "type": "expense",
            "category": "fertilizer purchase",
            "description": "Bought NPK fertilizer",
            "amount": 250.50,
            "parcel_id": 1,
            "activity_id": 5
        }
        transaction = TransactionCreate(**transaction_data)
        
        assert transaction.type == "expense"
        assert transaction.category == "fertilizer purchase"
        assert transaction.amount == 250.50
    
    def test_transaction_create_minimal(self):
        """Test creating TransactionCreate with minimal data."""
        transaction_data = {
            "date": date(2024, 7, 1),
            "type": "income",
            "category": "crop sales",
            "amount": 1000.0,
            "parcel_id": 2
        }
        transaction = TransactionCreate(**transaction_data)
        
        assert transaction.description is None
        assert transaction.activity_id is None


class TestBudgetSchemas:
    """Test Budget-related schemas."""
    
    def test_budget_create_valid(self):
        """Test creating a valid BudgetCreate schema."""
        budget_data = {
            "year": 2024,
            "category": "fertilizers",
            "estimated_amount": 5000.0,
            "parcel_id": 1
        }
        budget = BudgetCreate(**budget_data)
        
        assert budget.year == 2024
        assert budget.category == "fertilizers"
        assert budget.estimated_amount == 5000.0


class TestBiologicalParameterSchemas:
    """Test BiologicalParameter-related schemas."""
    
    def test_biological_parameter_create(self):
        """Test creating BiologicalParameterCreate schema."""
        param_data = {
            "name": "crop cycle",
            "value": 120.0,
            "unit": "days",
            "description": "Average corn growth cycle",
            "parcel_id": 1
        }
        param = BiologicalParameterCreate(**param_data)
        
        assert param.name == "crop cycle"
        assert param.value == 120.0
        assert param.unit == "days"


class TestSimulationSchemas:
    """Test Simulation-related schemas."""
    
    def test_simulation_create_valid(self):
        """Test creating a valid SimulationCreate schema."""
        simulation_data = {
            "name": "Crop Yield Projection",
            "description": "Simulating corn yield for next season",
            "creation_date": date(2024, 7, 1),
            "parameters": {
                "temperature": 25,
                "rainfall": 800,
                "fertilizer": 150
            },
            "results": {
                "yield": 5000,
                "quality": "high"
            },
            "user_id": 1
        }
        simulation = SimulationCreate(**simulation_data)
        
        assert simulation.name == "Crop Yield Projection"
        assert simulation.parameters["temperature"] == 25
        assert simulation.results["yield"] == 5000


class TestMiscellaneousSchemas:
    """Test miscellaneous schemas."""
    
    def test_chat_request(self):
        """Test ChatRequest schema."""
        chat_data = {"prompt": "What is the best time to plant corn?"}
        chat_request = ChatRequest(**chat_data)
        
        assert chat_request.prompt == "What is the best time to plant corn?"
    
    def test_change_history_create(self):
        """Test ChangeHistoryCreate schema."""
        history_data = {
            "table": "parcels",
            "field": "status",
            "previous_value": "active",
            "new_value": "maintenance",
            "date": date(2024, 7, 1),
            "user_id": 1,
            "reason": "Scheduled maintenance"
        }
        history = ChangeHistoryCreate(**history_data)
        
        assert history.table == "parcels"
        assert history.field == "status"
        assert history.reason == "Scheduled maintenance"
    
    def test_indicator_create(self):
        """Test IndicatorCreate schema."""
        indicator_data = {
            "name": "Crop Yield",
            "value": 4500.0,
            "unit": "kg/ha",
            "date": date(2024, 7, 1),
            "parcel_id": 1,
            "description": "Average corn yield"
        }
        indicator = IndicatorCreate(**indicator_data)
        
        assert indicator.name == "Crop Yield"
        assert indicator.value == 4500.0
        assert indicator.unit == "kg/ha"
