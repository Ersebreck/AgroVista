"""
Click detection utilities for map interactions
"""

from typing import Dict, List, Tuple, Optional
from .geospatial import get_location_coordinates


def point_in_polygon(point_lat: float, point_lng: float, polygon_coords: List[List[float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm
    
    Args:
        point_lat: Latitude of the point to check
        point_lng: Longitude of the point to check  
        polygon_coords: List of [lat, lon] coordinate pairs defining the polygon
        
    Returns:
        True if point is inside polygon, False otherwise
    """
    x, y = point_lng, point_lat
    n = len(polygon_coords)
    inside = False
    
    p1x, p1y = polygon_coords[0][1], polygon_coords[0][0]  # [lat, lon] -> [lon, lat]
    for i in range(1, n + 1):
        p2x, p2y = polygon_coords[i % n][1], polygon_coords[i % n][0]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def extract_click_coordinates(map_data: Dict) -> Optional[Tuple[float, float]]:
    """
    Extract click coordinates from st_folium map data
    
    Args:
        map_data: Dictionary returned by st_folium
        
    Returns:
        Tuple of (lat, lng) if click detected, None otherwise
    """
    clicked_lat = clicked_lng = None
    
    # Check last_object_clicked first
    if map_data and map_data.get('last_object_clicked'):
        clicked_obj = map_data['last_object_clicked']
        if isinstance(clicked_obj, dict) and clicked_obj.get('lat') and clicked_obj.get('lng'):
            clicked_lat = clicked_obj['lat']
            clicked_lng = clicked_obj['lng']
    
    # Fallback to last_clicked
    if not clicked_lat and map_data and map_data.get('last_clicked'):
        clicked_obj = map_data['last_clicked']
        if isinstance(clicked_obj, dict) and clicked_obj.get('lat') and clicked_obj.get('lng'):
            clicked_lat = clicked_obj['lat']
            clicked_lng = clicked_obj['lng']
    
    return (clicked_lat, clicked_lng) if clicked_lat and clicked_lng else None


def detect_clicked_parcel(click_coords: Tuple[float, float], parcels: List[Dict]) -> Optional[Dict]:
    """
    Detect which parcel was clicked based on coordinates
    
    Args:
        click_coords: Tuple of (lat, lng) coordinates
        parcels: List of parcel dictionaries
        
    Returns:
        Parcel dictionary if found, None otherwise
    """
    clicked_lat, clicked_lng = click_coords
    
    for parcel in parcels:
        if parcel.get('location_id'):
            coords = get_location_coordinates(parcel['location_id'])
            if coords and point_in_polygon(clicked_lat, clicked_lng, coords):
                return parcel
    return None


def detect_clicked_terrain(click_coords: Tuple[float, float], terrains: List[Dict]) -> Optional[Dict]:
    """
    Detect which terrain was clicked based on coordinates
    
    Args:
        click_coords: Tuple of (lat, lng) coordinates  
        terrains: List of terrain dictionaries
        
    Returns:
        Terrain dictionary if found, None otherwise
    """
    clicked_lat, clicked_lng = click_coords
    
    for terrain in terrains:
        if terrain.get('location_id'):
            coords = get_location_coordinates(terrain['location_id'])
            if coords and point_in_polygon(clicked_lat, clicked_lng, coords):
                return terrain
    return None


def process_map_click(map_data: Dict, terrains: List[Dict], parcels: List[Dict]) -> Dict:
    """
    Process a map click and return selection information
    
    Args:
        map_data: Dictionary returned by st_folium
        terrains: List of terrain dictionaries
        parcels: List of parcel dictionaries
        
    Returns:
        Dictionary with 'type', 'id', and 'data' keys for the selected item
    """
    click_coords = extract_click_coordinates(map_data)
    if not click_coords:
        return {'type': None, 'id': None, 'data': None}
    
    # Check parcels first (more specific)
    clicked_parcel = detect_clicked_parcel(click_coords, parcels)
    if clicked_parcel:
        return {
            'type': 'parcel',
            'id': clicked_parcel['id'],
            'data': clicked_parcel,
            'terrain_id': clicked_parcel.get('terrain_id')
        }
    
    # Check terrains if no parcel found
    clicked_terrain = detect_clicked_terrain(click_coords, terrains)
    if clicked_terrain:
        return {
            'type': 'terrain',
            'id': clicked_terrain['id'], 
            'data': clicked_terrain,
            'terrain_id': clicked_terrain['id']
        }
    
    return {'type': None, 'id': None, 'data': None}