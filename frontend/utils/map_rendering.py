"""
Map rendering utilities for AgroVista frontend
"""

import folium
from typing import List, Dict
from .geospatial import get_location_coordinates


def create_base_map(center_lat: float = 5.490471, center_lng: float = -74.682919, zoom: int = 15) -> folium.Map:
    """Create base Folium map with satellite imagery"""
    return folium.Map(location=[center_lat, center_lng], zoom_start=zoom, tiles='Esri.WorldImagery')


def add_terrain_polygons(map_obj: folium.Map, terrains_df, selected_terrain_id: int = None):
    """Add terrain polygons to the map"""
    terrain_colors = ["green", "blue", "orange", "purple"]
    
    for i, (_, row) in enumerate(terrains_df.iterrows()):
        if 'location_id' in row and row['location_id']:
            coords = get_location_coordinates(row['location_id'])
            if coords:
                feature = {
                    "type": "Feature",
                    "properties": {"name": row['name']},
                    "geometry": {"type": "Polygon", "coordinates": [[ [lon, lat] for lat, lon in coords ]]}
                }
                folium.GeoJson(
                    feature,
                    tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Terrain:"] ),
                    style_function=lambda x, color=terrain_colors[i%len(terrain_colors)]: {
                        "fillColor": color,
                        "color": "black",
                        "weight": 2,
                        "fillOpacity": 0.3,
                        "opacity": 0.8
                    }
                ).add_to(map_obj)


def add_parcel_polygons_and_markers(map_obj: folium.Map, parcels_df, statuses: Dict[int, List[str]], 
                                  status_converter_func, selected_parcel_id: int = None):
    """Add parcel polygons and status markers to the map"""
    status_emoji = {"Optimal": "✅", "Attention": "⚠️", "Critical": "🚨"}
    
    for _, row in parcels_df.iterrows():
        name = row['name']
        if 'location_id' in row and row['location_id']:
            coords = get_location_coordinates(row['location_id'])
            if coords:
                # Add parcel polygon
                feature = {
                    "type": "Feature",
                    "properties": {"name": name},
                    "geometry": {"type": "Polygon", "coordinates": [[ [lon, lat] for lat, lon in coords ]]}
                }
                folium.GeoJson(
                    feature,
                    tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Parcel:"] ),
                    style_function=lambda x: {
                        "fillColor": "lightgreen",
                        "color": "black",
                        "weight": 2,
                        "fillOpacity": 0.4,
                    }
                ).add_to(map_obj)
                
                # Add status marker
                center_lat = sum([p[0] for p in coords]) / len(coords)
                center_lon = sum([p[1] for p in coords]) / len(coords)
                
                # Get status and convert to display format
                status_raw = statuses.get(row['id'], ["Attention"])
                status_display = status_converter_func(status_raw)
                emoji = status_emoji.get(status_display, '❓')
                
                folium.Marker(
                    location=[center_lat, center_lon],
                    tooltip=f"{name} ({status_display})",
                    icon=folium.DivIcon(html=f"<div style='font-size:22px'>{emoji}</div>")
                ).add_to(map_obj)