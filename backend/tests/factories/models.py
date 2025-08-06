"""
Factory classes for generating test data.
"""
from datetime import datetime, timedelta
import factory
from factory import fuzzy
from faker import Faker

from app.models import (
    User, Terrain, Parcel, Activity, ActivityDetail,
    Location, Inventory, InventoryEvent, Transaction,
    Budget, BiologicalParameter, Simulation, ChangeHistory, Indicator
)

fake = Faker()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    name = factory.Faker("name")
    hashed_password = "hashed_test_password"
    created_at = factory.LazyFunction(datetime.utcnow)


class TerrainFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Terrain
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("city")
    description = factory.Faker("text", max_nb_chars=200)
    user = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class ParcelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parcel
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"Parcel {n}")
    description = factory.Faker("text", max_nb_chars=100)
    terrain = factory.SubFactory(TerrainFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class LocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Location
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"Location {n}")
    description = factory.Faker("text", max_nb_chars=100)
    parcel = factory.SubFactory(ParcelFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Activity
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=200)
    location = factory.SubFactory(LocationFactory)
    date = fuzzy.FuzzyDate(
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date() + timedelta(days=30)
    )
    activity_type = fuzzy.FuzzyChoice(["Maintenance", "Harvest", "Planting", "Treatment"])
    status = fuzzy.FuzzyChoice(["Planned", "In Progress", "Completed", "Cancelled"])
    created_at = factory.LazyFunction(datetime.utcnow)


class ActivityDetailFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ActivityDetail
        sqlalchemy_session_persistence = "commit"
    
    activity = factory.SubFactory(ActivityFactory)
    name = factory.Faker("word")
    value = factory.Faker("pystr", max_chars=50)
    unit = fuzzy.FuzzyChoice(["kg", "L", "units", "hours"])


class InventoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Inventory
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=100)
    unit = fuzzy.FuzzyChoice(["kg", "L", "units"])
    stock = fuzzy.FuzzyDecimal(0, 1000, 2)
    min_stock = fuzzy.FuzzyDecimal(0, 100, 2)
    user = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class InventoryEventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InventoryEvent
        sqlalchemy_session_persistence = "commit"
    
    inventory = factory.SubFactory(InventoryFactory)
    event_type = fuzzy.FuzzyChoice(["Entry", "Exit", "Adjustment"])
    quantity = fuzzy.FuzzyDecimal(-100, 100, 2)
    unit_price = fuzzy.FuzzyDecimal(0, 100, 2)
    observations = factory.Faker("text", max_nb_chars=100)
    created_at = factory.LazyFunction(datetime.utcnow)


class TransactionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Transaction
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    transaction_type = fuzzy.FuzzyChoice(["Income", "Expense"])
    category = fuzzy.FuzzyChoice(["Sales", "Purchases", "Labor", "Other"])
    amount = fuzzy.FuzzyDecimal(0, 10000, 2)
    date = fuzzy.FuzzyDate(
        start_date=datetime.now().date() - timedelta(days=90),
        end_date=datetime.now().date()
    )
    description = factory.Faker("text", max_nb_chars=100)
    parcel = factory.SubFactory(ParcelFactory)
    activity = factory.SubFactory(ActivityFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class BudgetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Budget
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    amount = fuzzy.FuzzyDecimal(1000, 50000, 2)
    budget_type = fuzzy.FuzzyChoice(["Annual", "Quarterly", "Monthly"])
    period = factory.LazyFunction(lambda: datetime.now().strftime("%Y"))
    parcel = factory.SubFactory(ParcelFactory)
    user = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
