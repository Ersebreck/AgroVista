"""
Geospatial utilities for AgroVista frontend
"""

import requests
from typing import Optional, List


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