import requests
import pandas as pd
from datetime import timedelta
from collections import Counter
from typing import Dict, List, Tuple, Any, Optional

API_URL = "http://localhost:8000"  # Adjust if running from Docker or different domain


def get_location_coordinates(location_id: int) -> Optional[List[List[float]]]:
    """
    Fetch coordinates from locations endpoint.
    
    Args:
        location_id: The ID of the location to fetch
        
    Returns:
        List of coordinate pairs [lat, lon] or None if error
    """
    try:
        response = requests.get(f"http://localhost:8000/locations/{location_id}")
        response.raise_for_status()
        location = response.json()
        
        # Extract coordinates from GeoJSON format
        if 'coordinates' in location and location['coordinates']:
            coords_geojson = location['coordinates']['coordinates'][0]  # Get first ring of polygon
            # Convert from [lon, lat] to [lat, lon] format for Folium
            coords_latlon = [[coord[1], coord[0]] for coord in coords_geojson]
            return coords_latlon
    except Exception as e:
        print(f"Error fetching coordinates for location {location_id}: {e}")
    return None


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


def evaluate_parcel_status(activities_df: pd.DataFrame) -> Dict[int, List[str]]:
    """
    Evaluate parcel status based on activity data.
    
    Args:
        activities_df: DataFrame with activity data
        
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

        if days_without_activity <= 5:
            status.append("Active")
        elif days_without_activity <= 10:
            status.append("Pending intervention")
        else:
            status.append("Inactive")

        if "Harvest" in group["type"].tolist() or "Cosecha" in group["type"].tolist():
            harvest_dates = group[group["type"].isin(["Harvest", "Cosecha"])]["date"]
            if any((today - harvest_dates).dt.days <= 3):
                status.append("Recently harvested")

        recent_tasks = group[group["date"] >= today - timedelta(days=3)]
        if len(recent_tasks) >= 3:
            status.append("High task load")

        if group["type"].isin(["Harvest", "Cosecha", "Milking", "Ordeño", "Weighing", "Pesaje"]).any():
            status.append("Has productivity")

        parcel_status[parcel_id] = status

    return parcel_status


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """
    Load all necessary data from backend.
    
    Returns:
        Tuple of (activities_df, parcels_df, terrains_df, parcel_name_to_id_map)
    """
    # Check backend connection
    try:
        terrains = get_terrains()
    except Exception as e:
        print(f"Error getting terrains: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
    
    parcels = []
    for terrain in terrains:
        parcels += get_parcels_by_terrain(terrain["id"])

    activities = []
    for parcel in parcels:
        acts = get_activities_by_parcel(parcel["id"])
        for act in acts:
            act["name"] = parcel["name"]
        activities += acts

    activities_df = pd.DataFrame(activities)
    activities_df["date"] = pd.to_datetime(activities_df["date"], errors="coerce")
    parcels_df = pd.DataFrame(parcels)
    terrains_df = pd.DataFrame(terrains)
    parcel_ids = {row["name"]: row["id"] for _, row in parcels_df.iterrows()}
    return activities_df, parcels_df, terrains_df, parcel_ids


def get_llm_response(prompt: str) -> str:
    """
    Get response from LLM chat endpoint.
    
    Args:
        prompt: The user prompt to send to the LLM
        
    Returns:
        LLM response string or error message
    """
    try:
        res = requests.post(
            f"{API_URL}/chat",
            json={"prompt": prompt},
            timeout=15
        )
        res.raise_for_status()
        return res.json().get("response", res.json().get("respuesta", "[No response from model]"))
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "[Error connecting to backend]"


def get_activities_by_parcel(parcel_id: int) -> List[Dict[str, Any]]:
    """Get activities for a specific parcel."""
    try:
        res = requests.get(f"{API_URL}/activities/by-parcel/{parcel_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error getting activities: {e}")
        return []


def get_terrains() -> List[Dict[str, Any]]:
    """Get all terrains."""
    try:
        res = requests.get(f"{API_URL}/terrains")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error getting terrains: {e}")
        return []


def get_parcels_by_terrain(terrain_id: int) -> List[Dict[str, Any]]:
    """Get parcels for a specific terrain."""
    try:
        res = requests.get(f"{API_URL}/parcels/by-terrain/{terrain_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error getting parcels: {e}")
        return []


def get_parcel(parcel_id: int) -> Dict[str, Any]:
    """Get a specific parcel by ID."""
    try:
        res = requests.get(f"{API_URL}/parcels/{parcel_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error getting parcel: {e}")
        return {}


def get_location(location_id: int) -> Dict[str, Any]:
    """Get a specific location by ID."""
    try:
        res = requests.get(f"{API_URL}/locations/{location_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error getting location: {e}")
        return {}


def register_activity(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Register a new activity."""
    try:
        res = requests.post(f"{API_URL}/activities/", json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error registering activity: {e}")
        return None


# Legacy function names for backwards compatibility
def resumen_estado_parcelas(estado_parcelas: Dict[int, List[str]]) -> Counter:
    """Legacy wrapper for summarize_parcel_status"""
    return summarize_parcel_status(estado_parcelas)


def evaluar_estado_parcelas(df_actividades: pd.DataFrame) -> Dict[int, List[str]]:
    """Legacy wrapper for evaluate_parcel_status"""
    return evaluate_parcel_status(df_actividades)


def cargar_datos() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """Legacy wrapper for load_data"""
    return load_data()


def obtener_respuesta_llm(prompt: str) -> str:
    """Legacy wrapper for get_llm_response"""
    return get_llm_response(prompt)


def obtener_actividades_por_parcela(parcela_id: int) -> List[Dict[str, Any]]:
    """Legacy wrapper for get_activities_by_parcel"""
    return get_activities_by_parcel(parcela_id)


def obtener_terrenos() -> List[Dict[str, Any]]:
    """Legacy wrapper for get_terrains"""
    return get_terrains()


def obtener_parcelas_por_terreno(terreno_id: int) -> List[Dict[str, Any]]:
    """Legacy wrapper for get_parcels_by_terrain"""
    return get_parcels_by_terrain(terreno_id)


def obtener_parcela(parcela_id: int) -> Dict[str, Any]:
    """Legacy wrapper for get_parcel"""
    return get_parcel(parcela_id)


def obtener_ubicacion(ubicacion_id: int) -> Dict[str, Any]:
    """Legacy wrapper for get_location"""
    return get_location(ubicacion_id)


def registrar_actividad(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Legacy wrapper for register_activity"""
    return register_activity(data)
