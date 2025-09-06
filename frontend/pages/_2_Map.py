import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from typing import List, Optional
from utils import load_data, evaluate_parcel_status, summarize_parcel_status


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


def obtener_coordenadas_ubicacion(ubicacion_id: int) -> Optional[List[List[float]]]:
    """Legacy wrapper for get_location_coordinates"""
    return get_location_coordinates(ubicacion_id)

st.title("Interactive Parcel Map")

# --- Load data from backend ---
df_activities, parcels_df, terrains_df, parcel_ids = load_data()

# --- Create base map ---
m = folium.Map(location=[5.490471, -74.682919], zoom_start=15, tiles='Esri.WorldImagery')

# --- Add terrains as polygons ---
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
                }
            ).add_to(m)

# --- Add parcels as polygons and markers with status ---
status_emoji = {"Optimal": "✅", "Attention": "⚠️", "Critical": "🚨"}
statuses = evaluate_parcel_status(df_activities)

def convert_status_to_display(status_list: List[str]) -> str:
    """
    Convert raw status list to display status.
    
    Args:
        status_list: List of status strings from parcel evaluation
        
    Returns:
        Display status string ("Optimal", "Attention", "Critical")
    """
    # Check for both English and Spanish statuses
    if "Inactive" in status_list or "Inactiva" in status_list:
        return "Critical"
    elif "Pending intervention" in status_list or "Pendiente de intervención" in status_list:
        return "Attention"
    elif "Active" in status_list or "Activa" in status_list:
        return "Optimal"
    else:
        return "Attention"


def convertir_estado_a_display(estados_lista: List[str]) -> str:
    """Legacy wrapper for convert_status_to_display"""
    return convert_status_to_display(estados_lista)

for _, row in parcels_df.iterrows():
    name = row['name']
    if 'location_id' in row and row['location_id']:
        coords = get_location_coordinates(row['location_id'])
        if coords:
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
            ).add_to(m)
            # Approximate center
            center_lat = sum([p[0] for p in coords]) / len(coords)
            center_lon = sum([p[1] for p in coords]) / len(coords)
            
            # Get raw status and convert to display format
            status_raw = statuses.get(row['id'], ["Attention"])
            status_display = convert_status_to_display(status_raw)
            emoji = status_emoji.get(status_display, '❓')
            
            folium.Marker(
                location=[center_lat, center_lon],
                tooltip=f"{name} ({status_display})",
                icon=folium.DivIcon(html=f"<div style='font-size:22px'>{emoji}</div>")
            ).add_to(m)

# --- Show map in Streamlit ---
st_folium(m, width=800, height=500)

# --- Sidebar status summary ---
with st.sidebar:
    st.markdown("### Parcel status summary")
    summary = summarize_parcel_status(statuses)
    st.write(f"✅ Optimal: {summary['Optimal']}")
    st.write(f"⚠️ Attention: {summary['Attention']}")
    st.write(f"🚨 Critical: {summary['Critical']}")
