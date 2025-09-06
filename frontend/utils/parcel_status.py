"""
Parcel status evaluation utilities
"""

import pandas as pd
from datetime import timedelta
from collections import Counter
from typing import Dict, List


def evaluate_parcel_status(activities_df: pd.DataFrame) -> Dict[int, List[str]]:
    """
    Evaluate parcel status based on activity data.
    
    Args:
        activities_df: DataFrame with activity data
        
    Returns:
        Dictionary mapping parcel_id to list of status strings
    """
    if activities_df.empty:
        return {}
        
    today = pd.Timestamp.today().normalize()
    parcel_status = {}

    for parcel_id, group in activities_df.groupby("parcel_id"):
        group = group.copy()
        group["date"] = pd.to_datetime(group["date"], errors="coerce")

        last_date = group["date"].max()
        if pd.isna(last_date):
            parcel_status[parcel_id] = ["Inactive"]
            continue
            
        days_without_activity = (today - last_date).days
        status = []

        # Activity recency status
        if days_without_activity <= 5:
            status.append("Active")
        elif days_without_activity <= 10:
            status.append("Pending intervention")
        else:
            status.append("Inactive")

        # Recent harvest check
        if "Harvest" in group["type"].tolist() or "Cosecha" in group["type"].tolist():
            harvest_dates = group[group["type"].isin(["Harvest", "Cosecha"])]["date"]
            if any((today - harvest_dates).dt.days <= 3):
                status.append("Recently harvested")

        # High task load check
        recent_tasks = group[group["date"] >= today - timedelta(days=3)]
        if len(recent_tasks) >= 3:
            status.append("High task load")

        # Productivity check
        if group["type"].isin(["Harvest", "Cosecha", "Milking", "Ordeño", "Weighing", "Pesaje"]).any():
            status.append("Has productivity")

        parcel_status[parcel_id] = status

    return parcel_status


def summarize_parcel_status(parcel_status: Dict[int, List[str]]) -> Counter:
    """
    Summarize parcel statuses into display categories.
    
    Args:
        parcel_status: Dictionary mapping parcel_id to list of status strings
        
    Returns:
        Counter with counts for different status categories
    """
    summary = Counter({"Optimal": 0, "Attention": 0, "Critical": 0})
    for statuses in parcel_status.values():
        if "Inactive" in statuses or "Inactiva" in statuses:
            summary["Critical"] += 1
        elif "Pending intervention" in statuses or "Pendiente de intervención" in statuses:
            summary["Attention"] += 1
        elif "Active" in statuses or "Activa" in statuses:
            summary["Optimal"] += 1
        else:
            summary["Attention"] += 1
    return summary

