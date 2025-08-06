from datetime import date, timedelta

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from sqlalchemy.orm import Session

from app.models import (
    Activity,
    ActivityDetail,
    Indicator,
    Inventory,
    InventoryEvent,
    Location,
    Parcel,
    Terrain,
    Transaction,
    User,
)


def create_users(db: Session) -> User:
    """Create default users for the database."""
    admin = User(
        name="Admin", email="admin@agro.com", password="admin123", role="admin"
    )
    owner = User(
        name="Demo Owner", email="prop@agro.com", password="demo123", role="owner"
    )
    db.add_all([admin, owner])
    db.commit()
    return owner


def create_terrains_and_parcels(db: Session, owner: User) -> None:
    """Create terrains and parcels with real coordinates and deterministic status."""
    today = date.today()

    terrain_coords = {
        "Terreno 1": [
            [5.490012, -74.689513],
            [5.491388, -74.686458],
            [5.493076, -74.686186],
            [5.494909, -74.687275],
            [5.495821, -74.687296],
            [5.495455, -74.689642],
            [5.492761, -74.690266],
        ],
        "Terreno 2": [
            [5.490012, -74.689513],
            [5.491388, -74.686458],
            [5.489541, -74.683064],
            [5.485220, -74.683948],
            [5.487558, -74.688777],
        ],
    }

    parcel_coords = {
        "Parcela 1A": [
            [5.490012, -74.689513],
            [5.490818, -74.687843],
            [5.493041, -74.688052],
            [5.492761, -74.690266],
        ],
        "Parcela 1B": [
            [5.493021, -74.688042],
            [5.493201, -74.686225],
            [5.494670, -74.687154],
            [5.495789, -74.687333],
            [5.495671, -74.688349],
        ],
        "Parcela 2A": [
            [5.488324, -74.685804],
            [5.486298, -74.686302],
            [5.485390, -74.683935],
            [5.487827, -74.683315],
        ],
        "Parcela 2B": [
            [5.488324, -74.685804],
            [5.487951, -74.683294],
            [5.489582, -74.683106],
            [5.490635, -74.685222],
        ],
    }

    # Status: 2 optimal, 1 attention needed, 1 critical
    parcel_info = {
        # Parcels in optimal status (active with few days without activity)
        "Parcela 1A": {
            "uso": "Young cane",
            "estado": "activo",
            "dias_sin_actividad": 1,
            "estado_salud": "optimal",
        },
        "Parcela 1B": {
            "uso": "Sugar cane",
            "estado": "activo",
            "dias_sin_actividad": 2,
            "estado_salud": "optimal",
        },
        # Parcel needing attention (some indicator out of range)
        "Parcela 2A": {
            "uso": "Pasture",
            "estado": "activo",
            "dias_sin_actividad": 5,
            "estado_salud": "attention",
        },
        # Parcel in critical status (long time without maintenance)
        "Parcela 2B": {
            "uso": "Pens",
            "estado": "mantenimiento",
            "dias_sin_actividad": 15,
            "estado_salud": "critical",
        },
    }

    terrain_objects = {}
    for name, coords in terrain_coords.items():
        polygon = Polygon([(lon, lat) for lat, lon in coords])
        location = Location(
            type="polygon",
            coordinates=from_shape(polygon, srid=4326),
            reference={"name": name},
        )
        db.add(location)
        db.commit()

        terrain = Terrain(
            name=name,
            description="Terrain generated with real coordinates.",
            owner_id=owner.id,
            location_id=location.id,
        )
        db.add(terrain)
        db.commit()
        terrain_objects[name] = terrain

    for i, (name, coords) in enumerate(parcel_coords.items(), start=1):
        terrain_id = 1 if "1" in name else 2
        info = parcel_info[name]
        polygon = Polygon([(lon, lat) for lat, lon in coords])
        location = Location(
            type="polygon",
            coordinates=from_shape(polygon, srid=4326),
            reference={"name": name},
        )
        db.add(location)
        db.commit()

        parcel = Parcel(
            name=name,
            current_use=info["uso"],
            status=info["estado"],
            terrain_id=terrain_objects[f"Terreno {terrain_id}"].id,
            location_id=location.id,
        )
        db.add(parcel)
        db.commit()

        base_date = today - timedelta(days=info["dias_sin_actividad"])

        # Define activities according to parcel health status
        if info["estado_salud"] == "optimal":
            # Optimal parcels have recent activities in good condition
            activities = [
                (
                    "Irrigation",
                    base_date - timedelta(hours=2),
                    "Scheduled irrigation",
                    "200",
                    "l",
                ),
                (
                    "Fertilization",
                    base_date - timedelta(days=1),
                    "Fertilizer application",
                    "30",
                    "kg",
                ),
                (
                    "Harvest",
                    base_date - timedelta(days=3),
                    "Partial harvest",
                    "1000",
                    "kg",
                ),
            ]
        elif info["estado_salud"] == "attention":
            # Parcel needing attention has more spaced activities
            activities = [
                (
                    "Irrigation",
                    base_date - timedelta(days=2),
                    "Insufficient irrigation",
                    "100",
                    "l",
                ),
                (
                    "Fertilization",
                    base_date - timedelta(days=7),
                    "Pending fertilization",
                    "20",
                    "kg",
                ),
                (
                    "Maintenance",
                    base_date - timedelta(days=10),
                    "Review needed",
                    "1",
                    "review",
                ),
            ]
        else:  # critical status
            # Critical parcel has very old or missing activities
            activities = [
                (
                    "Irrigation",
                    base_date - timedelta(days=14),
                    "Last irrigation",
                    "50",
                    "l",
                ),
                (
                    "Maintenance",
                    base_date - timedelta(days=30),
                    "Urgent maintenance required",
                    "1",
                    "urgency",
                ),
            ]

        # Create the activities
        for activity_type, activity_date, desc, value, unit in activities:
            activity = Activity(
                type=activity_type,
                date=activity_date,
                description=desc,
                user_id=owner.id,
                parcel_id=parcel.id,
            )
            db.add(activity)
            db.flush()  # To get the activity ID

            # Create specific details for each activity type
            detail = None
            if activity_type == "Fertilization":
                detail = ActivityDetail(
                    name="NPK Fertilizer",
                    value=value,
                    unit=unit,
                    activity_id=activity.id,
                )
            elif activity_type == "Harvest":
                detail = ActivityDetail(
                    name="Kg harvested", value=value, unit=unit, activity_id=activity.id
                )
            elif activity_type == "Irrigation":
                detail = ActivityDetail(
                    name="Water used", value=value, unit=unit, activity_id=activity.id
                )
            elif activity_type == "Maintenance":
                detail = ActivityDetail(
                    name="Status", value=desc, unit=unit, activity_id=activity.id
                )

            if detail:
                db.add(detail)

        db.commit()

    # --------------------------
    # NEW ENTITIES
    # --------------------------
    created_parcels = db.query(Parcel).all()

    # Deterministic transactions according to health status
    transactions_by_status = {
        "optimal": [
            {
                "tipo": "ingreso",
                "categoria": "Corn sales",
                "descripcion": "Income from corn sales",
                "monto": 1800,
            },
            {
                "tipo": "gasto",
                "categoria": "Fertilizer purchase",
                "descripcion": "NPK fertilizer purchase",
                "monto": 200,
            },
        ],
        "attention": [
            {
                "tipo": "gasto",
                "categoria": "Mechanized irrigation",
                "descripcion": "Additional irrigation due to drought",
                "monto": 500,
            },
            {
                "tipo": "gasto",
                "categoria": "Machinery maintenance",
                "descripcion": "Machinery repair",
                "monto": 400,
            },
            {
                "tipo": "ingreso",
                "categoria": "Milk sales",
                "descripcion": "Low income due to low production",
                "monto": 600,
            },
        ],
        "critical": [
            {
                "tipo": "gasto",
                "categoria": "Machinery maintenance",
                "descripcion": "Urgent infrastructure repair",
                "monto": 900,
            },
            {
                "tipo": "gasto",
                "categoria": "Animal feed purchase",
                "descripcion": "Emergency feed purchase",
                "monto": 700,
            },
        ],
    }
    today = date.today()
    for parcel in created_parcels:
        health_status = None
        # Determine the health status of the parcel
        for name, info in parcel_info.items():
            if parcel.name == name:
                health_status = info["estado_salud"]
                break
        if not health_status:
            health_status = "optimal"  # fallback
        transactions = transactions_by_status.get(health_status, [])
        for idx, trans in enumerate(transactions):
            db.add(
                Transaction(
                    parcel_id=parcel.id,
                    date=today - timedelta(days=idx * 5),
                    type=trans["tipo"],
                    category=trans["categoria"],
                    description=trans["descripcion"],
                    amount=trans["monto"],
                )
            )
    db.commit()

    # Deterministic inventory and events according to health status
    inventory_by_status = {
        "optimal": [
            {
                "nombre": "NPK Fertilizer",
                "tipo": "Fertilizer",
                "cantidad_actual": 400,
                "unidad": "kg",
            },
            {
                "nombre": "Livestock feed",
                "tipo": "Feed",
                "cantidad_actual": 300,
                "unidad": "kg",
            },
        ],
        "attention": [
            {
                "nombre": "NPK Fertilizer",
                "tipo": "Fertilizer",
                "cantidad_actual": 150,
                "unidad": "kg",
            },
            {
                "nombre": "Livestock feed",
                "tipo": "Feed",
                "cantidad_actual": 100,
                "unidad": "kg",
            },
        ],
        "critical": [
            {
                "nombre": "NPK Fertilizer",
                "tipo": "Fertilizer",
                "cantidad_actual": 30,
                "unidad": "kg",
            },
            {
                "nombre": "Livestock feed",
                "tipo": "Feed",
                "cantidad_actual": 10,
                "unidad": "kg",
            },
        ],
    }
    events_by_status = {
        "optimal": [
            {"tipo_movimiento": "salida", "cantidad": 30, "observacion": "Regular use"}
        ],
        "attention": [
            {
                "tipo_movimiento": "salida",
                "cantidad": 60,
                "observacion": "High consumption",
            }
        ],
        "critical": [
            {
                "tipo_movimiento": "salida",
                "cantidad": 90,
                "observacion": "Critical consumption",
            }
        ],
    }
    inventory_id_map = {}
    inventory_id_counter = 1
    today = date.today()
    for parcel in created_parcels:
        health_status = None
        for name, info in parcel_info.items():
            if parcel.name == name:
                health_status = info["estado_salud"]
                break
        if not health_status:
            health_status = "optimal"
        inventories = inventory_by_status.get(health_status, [])
        for inv in inventories:
            inv_obj = Inventory(
                name=inv["nombre"],
                type=inv["tipo"],
                current_quantity=inv["cantidad_actual"],
                unit=inv["unidad"],
                parcel_id=parcel.id,
            )
            db.add(inv_obj)
            db.flush()
            inventory_id_map[inventory_id_counter] = inv_obj.id
            inventory_id_counter += 1
        events = events_by_status.get(health_status, [])
        for ev in events:
            db.add(
                InventoryEvent(
                    inventory_id=inv_obj.id,
                    activity_id=None,
                    movement_type=ev["tipo_movimiento"],
                    quantity=ev["cantidad"],
                    date=today - timedelta(days=2),
                    observation=ev["observacion"],
                )
            )
    db.commit()

    # Deterministic indicators according to health status
    indicators_by_status = {
        "optimal": [
            {
                "nombre": "Operational progress",
                "valor": 98,
                "unidad": "%",
                "descripcion": "Everything up to date",
            },
            {
                "nombre": "Cumulative production",
                "valor": 2500,
                "unidad": "kg",
                "descripcion": "Maximum production",
            },
        ],
        "attention": [
            {
                "nombre": "Operational progress",
                "valor": 70,
                "unidad": "%",
                "descripcion": "Some pending tasks",
            },
            {
                "nombre": "Cumulative production",
                "valor": 1200,
                "unidad": "kg",
                "descripcion": "Average production",
            },
        ],
        "critical": [
            {
                "nombre": "Operational progress",
                "valor": 30,
                "unidad": "%",
                "descripcion": "Critical tasks not performed",
            },
            {
                "nombre": "Cumulative production",
                "valor": 200,
                "unidad": "kg",
                "descripcion": "Very low production",
            },
        ],
    }
    for parcel in created_parcels:
        health_status = None
        for name, info in parcel_info.items():
            if parcel.name == name:
                health_status = info["estado_salud"]
                break
        if not health_status:
            health_status = "optimal"
        indicators = indicators_by_status.get(health_status, [])
        for ind in indicators:
            db.add(
                Indicator(
                    parcel_id=parcel.id,
                    name=ind["nombre"],
                    value=ind["valor"],
                    unit=ind["unidad"],
                    date=today,
                    description=ind["descripcion"],
                )
            )
    db.commit()

    print(
        "✅ Database populated with activities, inventory, transactions and indicators."
    )


# ----------------------
# LEGACY FUNCTION NAMES (Spanish names for backwards compatibility)
# ----------------------

create_terrenos_y_parcelas = create_terrains_and_parcels
