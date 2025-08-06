import re
import uuid
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd


def summarize_parcel_status(parcel_status: Dict[int, List[str]]) -> Counter:
    """
    Summarize parcel statuses into display categories.

    Args:
        parcel_status: Dictionary mapping parcel_id to list of status strings

    Returns:
        Counter with counts for "Optimal", "Attention", "Critical" categories
    """
    summary = Counter({"Optimal": 0, "Attention": 0, "Critical": 0})
    for statuses in parcel_status.values():
        if "Inactive" in statuses:
            summary["Critical"] += 1
        elif "Pending intervention" in statuses:
            summary["Attention"] += 1
        elif "Active" in statuses:
            summary["Optimal"] += 1
        else:
            summary["Attention"] += 1
    return summary


def evaluate_parcel_status(activities_df: pd.DataFrame) -> Dict[int, List[str]]:
    """
    Evaluate parcel status based on activity data.

    Args:
        activities_df: DataFrame with columns: parcel_id, date, type

    Returns:
        Dictionary mapping parcel_id to list of status strings
    """
    today = pd.Timestamp.today().normalize()
    parcel_status = {}

    for parcel_id, group in activities_df.groupby("parcel_id"):
        group = group.copy()
        group["date"] = pd.to_datetime(group["date"], errors="coerce")

        last_date = group["date"].max()
        days_without_activity = (today - last_date).days
        status = []

        # Activity recency status
        if days_without_activity <= 5:
            status.append("Active")
        elif days_without_activity <= 10:
            status.append("Pending intervention")
        else:
            status.append("Inactive")

        # Recent harvest status
        if "Harvest" in group["type"].tolist():
            harvest_dates = group[group["type"] == "Harvest"]["date"]
            if any((today - harvest_dates).dt.days <= 3):
                status.append("Recently harvested")

        # High task load status
        recent_tasks = group[group["date"] >= today - timedelta(days=3)]
        if len(recent_tasks) >= 3:
            status.append("High task load")

        # Productivity status
        if group["type"].isin(["Harvest", "Milking", "Weighing"]).any():
            status.append("Has productivity")

        parcel_status[parcel_id] = status

    return parcel_status


# Date utilities
def get_current_date() -> str:
    """Get current date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


def format_date(date_input: Union[datetime, str]) -> str:
    """Format date to YYYY-MM-DD string."""
    if isinstance(date_input, str):
        return date_input
    return date_input.strftime("%Y-%m-%d")


def calculate_days_difference(
    date1: Union[datetime, str], date2: Union[datetime, str]
) -> int:
    """Calculate difference in days between two dates."""
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, "%Y-%m-%d")
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, "%Y-%m-%d")
    return (date2 - date1).days


def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate that start_date <= end_date."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return start <= end


# Status utilities
def get_status_color(status: str) -> str:
    """Get color code for status."""
    status_colors = {
        "Completed": "green",
        "In Progress": "yellow",
        "Planned": "blue",
        "Cancelled": "red",
    }
    return status_colors.get(status, "gray")


def generate_summary_text(data: Dict[str, Any]) -> str:
    """Generate summary text from data dictionary."""
    return f"Total: {data.get('total', 0)}, Completed: {data.get('completed', 0)}, Pending: {data.get('pending', 0)}"


# Number utilities
def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage with 2 decimal places."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


# String utilities
def generate_unique_id() -> str:
    """Generate unique ID string."""
    return str(uuid.uuid4())


def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_string(text: Optional[str]) -> str:
    """Sanitize string by removing extra whitespace."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text.strip())


# Activity utilities
def calculate_days_without_activity(last_activity_date: Optional[datetime]) -> int:
    """Calculate days since last activity."""
    if last_activity_date is None:
        return -1
    return (datetime.now() - last_activity_date).days


def get_activity_status_icon(status: str) -> str:
    """Get icon for activity status."""
    icons = {"Completed": "✓", "In Progress": "⚡", "Planned": "📅", "Cancelled": "✗"}
    return icons.get(status, "?")


# Data validation utilities
def validate_positive_number(value: Any) -> bool:
    """Validate that value is a positive number (only numeric types)."""
    if not isinstance(value, (int, float)):
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def validate_percentage(value: float) -> bool:
    """Validate that value is a valid percentage (0-100)."""
    try:
        return 0 <= float(value) <= 100
    except (TypeError, ValueError):
        return False


# Conversion utilities
def convert_area_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between area units."""
    # Convert to square meters first
    to_m2 = {
        "m2": 1,
        "ha": 10000,
    }

    if from_unit not in to_m2 or to_unit not in to_m2:
        return value

    m2_value = value * to_m2[from_unit]
    return m2_value / to_m2[to_unit]


def convert_weight_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between weight units."""
    # Convert to grams first
    to_grams = {
        "g": 1,
        "kg": 1000,
        "t": 1000000,
        "lb": 453.592,
    }

    if from_unit not in to_grams or to_unit not in to_grams:
        return value

    gram_value = value * to_grams[from_unit]
    return gram_value / to_grams[to_unit]


# Legacy function names for backwards compatibility
def resumen_estado_parcelas(estado_parcelas: Dict[int, List[str]]) -> Counter:
    """Legacy wrapper for summarize_parcel_status"""
    return summarize_parcel_status(estado_parcelas)


def evaluar_estado_parcelas(df_actividades: pd.DataFrame) -> Dict[int, List[str]]:
    """Legacy wrapper for evaluate_parcel_status"""
    return evaluate_parcel_status(df_actividades)
