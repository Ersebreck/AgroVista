"""
Data loading utilities for AgroVista frontend
"""

import pandas as pd
import requests
from typing import Tuple, Dict


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """
    Load all necessary data from backend using working endpoints.
    
    Returns:
        Tuple of (activities_df, parcels_df, terrains_df, parcel_name_to_id_map)
    """
    base_url = "http://localhost:8000"
    
    # Load terrains using working endpoint
    try:
        response = requests.get(f"{base_url}/terrains")
        response.raise_for_status()
        terrains = response.json() or []
    except Exception as e:
        print(f"Error getting terrains: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
    
    # Load parcels for all terrains using working endpoint
    parcels = []
    for terrain in terrains:
        try:
            response = requests.get(f"{base_url}/parcels/by-terrain/{terrain['id']}")
            response.raise_for_status()
            terrain_parcels = response.json() or []
            parcels += terrain_parcels
        except Exception as e:
            print(f"Error getting parcels for terrain {terrain['id']}: {e}")

    # Load activities for all parcels using working endpoint
    activities = []
    for parcel in parcels:
        try:
            response = requests.get(f"{base_url}/activities/by-parcel/{parcel['id']}")
            response.raise_for_status()
            parcel_activities = response.json() or []
            for act in parcel_activities:
                act["name"] = parcel["name"]
            activities += parcel_activities
        except Exception as e:
            print(f"Error getting activities for parcel {parcel['id']}: {e}")

    # Create DataFrames
    activities_df = pd.DataFrame(activities)
    if not activities_df.empty:
        activities_df["date"] = pd.to_datetime(activities_df["date"], errors="coerce")
        
    parcels_df = pd.DataFrame(parcels)
    terrains_df = pd.DataFrame(terrains)
    
    # Create parcel name to ID mapping
    parcel_ids = {}
    if not parcels_df.empty:
        parcel_ids = {row["name"]: row["id"] for _, row in parcels_df.iterrows()}
    
    return activities_df, parcels_df, terrains_df, parcel_ids

