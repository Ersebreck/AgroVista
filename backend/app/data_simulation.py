import random
from datetime import date, timedelta
from typing import Any, Dict, List, Tuple

import pandas as pd

# ----------------------
# STATIC BASE DATA
# ----------------------

terrains = pd.DataFrame(
    [
        {"id": 1, "name": "Terrain 1", "description": "Mixed vegetable cultivation"},
        {"id": 2, "name": "Terrain 2", "description": "Livestock and forage"},
    ]
)

parcels = pd.DataFrame(
    [
        {
            "id": 1,
            "name": "Parcel 1A",
            "terrain_id": 1,
            "current_use": "Young corn",
            "status": "active",
            "days_without_activity": 1,
        },
        {
            "id": 2,
            "name": "Parcel 1B",
            "terrain_id": 1,
            "current_use": "Greenhouse tomato",
            "status": "active",
            "days_without_activity": 2,
        },
        {
            "id": 3,
            "name": "Parcel 2A",
            "terrain_id": 2,
            "current_use": "Pasture",
            "status": "active",
            "days_without_activity": 7,
        },
        {
            "id": 4,
            "name": "Parcel 2B",
            "terrain_id": 2,
            "current_use": "Pens",
            "status": "maintenance",
            "days_without_activity": 12,
        },
    ]
)

parcel_info = {
    "Terrain 1": " Mixed corn and tomato cultivation.",
    "Parcel 1A": " Young corn.",
    "Parcel 1B": " Greenhouse tomato.",
    "Terrain 2": " Livestock and forage zone.",
    "Parcel 2A": " Rotation pasture.",
    "Parcel 2B": " Maintenance pens.",
}

activity_types = [
    "Irrigation",
    "Fertilization",
    "Fumigation",
    "Harvest",
    "Planting",
    "Cleaning",
    "Weighing",
    "Vaccination",
    "Milking",
]

# Legacy variables for backwards compatibility
terrenos = terrains
parcelas = parcels
parcelas_info = parcel_info
tipos_actividad = activity_types

# Column name mappings for backward compatibility
terrain_column_mapping = {"nombre": "name", "descripcion": "description"}
parcel_column_mapping = {
    "nombre": "name",
    "terreno_id": "terrain_id",
    "uso_actual": "current_use",
    "estado": "status",
    "dias_sin_actividad": "days_without_activity",
}

# ----------------------
# SIMULATION FUNCTIONS
# ----------------------


def generate_activity(
    parcel_id: int, parcel_name: str, base_date: date, quantity: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate simulated activities for a parcel.

    Args:
        parcel_id: ID of the parcel
        parcel_name: Name of the parcel
        base_date: Base date for activity generation
        quantity: Number of activities to generate

    Returns:
        List of activity dictionaries
    """
    activities = []
    for i in range(quantity):
        activity_type = random.choice(activity_types)
        activity_date = base_date - timedelta(days=i)
        activities.append(
            {
                "parcel_id": parcel_id,
                "name": parcel_name,
                "type": activity_type,
                "description": f"{activity_type} performed in field",
                "date": activity_date,
            }
        )
    return activities


def generate_activity_details(activities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate detailed information for activities.

    Args:
        activities_df: DataFrame containing activities

    Returns:
        DataFrame with activity details
    """
    details = []

    for activity in activities_df.itertuples():
        activity_type = getattr(activity, "type", getattr(activity, "tipo", None))
        if activity_type == "Fertilization":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "NPK Fertilizer",
                    "value": 50,
                    "unit": "kg",
                }
            )
        elif activity_type == "Harvest":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "Kg harvested",
                    "value": random.randint(800, 1500),
                    "unit": "kg",
                }
            )
        elif activity_type == "Irrigation":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "Water used",
                    "value": random.randint(200, 800),
                    "unit": "l",
                }
            )
        elif activity_type == "Weighing":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "Livestock weight",
                    "value": random.randint(300, 600),
                    "unit": "kg",
                }
            )
        elif activity_type == "Vaccination":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "Vaccine applied",
                    "value": "Foot and Mouth",
                    "unit": "dose",
                }
            )
        elif activity_type == "Milking":
            details.append(
                {
                    "activity_id": activity.id,
                    "name": "Liters milked",
                    "value": random.randint(10, 30),
                    "unit": "l",
                }
            )

    return pd.DataFrame(details)


# Legacy function names for backwards compatibility
def generar_actividad(
    parcela_id: int, nombre_parcela: str, fecha_base: date, cantidad: int = 5
) -> List[Dict[str, Any]]:
    """Legacy wrapper for generate_activity"""
    return generate_activity(parcela_id, nombre_parcela, fecha_base, cantidad)


def generar_detalles(df_actividades: pd.DataFrame) -> pd.DataFrame:
    """Legacy wrapper for generate_activity_details"""
    return generate_activity_details(df_actividades)


# ----------------------
# TRANSACTION SIMULATION
# ----------------------


def simulate_transactions(
    parcels_df: pd.DataFrame, transactions_per_parcel: int = 3
) -> pd.DataFrame:
    """
    Simulate financial transactions for parcels.

    Args:
        parcels_df: DataFrame containing parcel information
        transactions_per_parcel: Number of transactions to generate per parcel

    Returns:
        DataFrame with simulated transactions
    """
    expense_categories = [
        "Fertilizer purchase",
        "Mechanized irrigation",
        "Machinery maintenance",
        "Animal feed purchase",
    ]
    income_categories = ["Corn sales", "Milk sales", "Livestock sales"]
    categories = ["Material supplies", "Labor", "Maintenance", "Consulting", "Others"]
    today = date.today()
    transactions = []

    for _, parcel in parcels_df.iterrows():
        for _ in range(transactions_per_parcel):
            transaction_type = random.choice(["expense", "income"])
            category = random.choice(
                income_categories
                if transaction_type == "income"
                else expense_categories
            )
            amount = (
                round(random.uniform(100, 1000), 2)
                if transaction_type == "expense"
                else round(random.uniform(500, 2000), 2)
            )

            transactions.append(
                {
                    "parcel_id": parcel["id"],
                    "date": today - timedelta(days=random.randint(1, 60)),
                    "type": transaction_type,
                    "category": category,
                    "description": f"{transaction_type.capitalize()} automatically recorded",
                    "amount": amount,
                }
            )

    for _, parcel in parcels_df.iterrows():
        for _ in range(transactions_per_parcel):
            category = random.choice(categories)
            amount = round(random.uniform(100, 5000), 2)
            is_income = random.choice([True, False])
            transaction_date = today - timedelta(days=random.randint(1, 90))

            transactions.append(
                {
                    "parcel_id": parcel["id"],
                    "concept": f"{category} {'income' if is_income else 'expense'}",
                    "amount": amount if is_income else -amount,
                    "date": transaction_date,
                    "category": category,
                    "type": "income" if is_income else "expense",
                }
            )

    return pd.DataFrame(transactions).sort_values("date", ascending=False)


# Legacy function for backwards compatibility
def simular_transacciones(
    parcelas_df: pd.DataFrame, n_por_parcela: int = 3
) -> pd.DataFrame:
    """Legacy wrapper for simulate_transactions"""
    return simulate_transactions(parcelas_df, n_por_parcela)


# ----------------------
# INVENTORY SIMULATION
# ----------------------


def simulate_inventory(parcels_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simulate inventory and inventory events for parcels.

    Args:
        parcels_df: DataFrame containing parcel information

    Returns:
        Tuple of (inventory_df, events_df)
    """
    supply_types = ["NPK Fertilizer", "Livestock feed", "Bovine vaccine", "Pesticide"]
    inventory = []
    events = []
    id_counter = 1
    today = date.today()

    for _, parcel in parcels_df.iterrows():
        for supply in supply_types:
            quantity = round(random.uniform(50, 500), 2)
            unit = (
                "kg"
                if "Fertilizer" in supply
                else "l"
                if "Pesticide" in supply
                else "dose"
            )
            inventory.append(
                {
                    "id": id_counter,
                    "name": supply,
                    "type": supply.split()[0],
                    "current_quantity": quantity,
                    "unit": unit,
                    "parcel_id": parcel["id"],
                }
            )

            # Create a consumption event
            events.append(
                {
                    "inventory_id": id_counter,
                    "activity_id": None,
                    "movement_type": "outbound",
                    "quantity": round(random.uniform(5, 30), 2),
                    "date": today - timedelta(days=random.randint(1, 20)),
                    "observation": "Routine consumption",
                }
            )
            id_counter += 1

    return pd.DataFrame(inventory), pd.DataFrame(events)


# Legacy function for backwards compatibility
def simular_inventario(parcelas_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Legacy wrapper for simulate_inventory"""
    return simulate_inventory(parcelas_df)


# ----------------------
# INDICATORS SIMULATION
# ----------------------


def simulate_indicators(parcels_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulate performance indicators for parcels.

    Args:
        parcels_df: DataFrame containing parcel information

    Returns:
        DataFrame with simulated indicators
    """
    indicators = []
    today = date.today()

    for _, parcel in parcels_df.iterrows():
        indicators += [
            {
                "parcel_id": parcel["id"],
                "name": "Operational progress",
                "value": round(random.uniform(60, 100), 1),
                "unit": "%",
                "date": today,
                "description": "Percentage of tasks completed this month",
            },
            {
                "parcel_id": parcel["id"],
                "name": "Cumulative production",
                "value": round(random.uniform(800, 3000), 2),
                "unit": "kg",
                "date": today,
                "description": "Estimated harvested volume",
            },
        ]

    return pd.DataFrame(indicators)


# ----------------------
# MAIN SIMULATION FUNCTION
# ----------------------


def simulate_data(
    parcels_df: pd.DataFrame,
) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """
    Generate complete simulated agricultural data.

    Args:
        parcels_df: DataFrame containing parcel information

    Returns:
        Tuple of (activities_df, details_df, transactions_df, inventory_df, events_df, indicators_df)
    """
    today = date.today()
    activities = []

    for _, row in parcels_df.iterrows():
        # Handle both old and new column names for backward compatibility
        days_inactive = row.get(
            "days_without_activity", row.get("dias_sin_actividad", 0)
        )
        parcel_name = row.get("name", row.get("nombre", ""))
        base_date = today - timedelta(days=days_inactive)
        activities += generate_activity(row["id"], parcel_name, base_date)

    activities_df = pd.DataFrame(activities).reset_index(drop=True)
    activities_df["id"] = activities_df.index + 1
    # Handle both old and new column names
    if "date" in activities_df.columns:
        activities_df["date"] = pd.to_datetime(activities_df["date"])
    elif "fecha" in activities_df.columns:
        activities_df["fecha"] = pd.to_datetime(activities_df["fecha"])

    transactions_df = simulate_transactions(parcels)
    inventory_df, events_df = simulate_inventory(parcels)
    indicators_df = simulate_indicators(parcels)
    details_df = generate_activity_details(activities_df)

    return (
        activities_df,
        details_df,
        transactions_df,
        inventory_df,
        events_df,
        indicators_df,
    )


# Legacy function for backwards compatibility
def simular_datos(
    parcelas_df: pd.DataFrame,
) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """Legacy wrapper for simulate_data"""
    return simulate_data(parcelas_df)
