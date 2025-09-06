import streamlit as st
from streamlit_folium import st_folium
from utils.data_loader import load_data
from utils.parcel_status import evaluate_parcel_status
from utils.map_rendering import create_base_map, add_terrain_polygons, add_parcel_polygons_and_markers
from utils.click_detection import process_map_click
from utils.status_utils import convert_status_to_display
from utils.sidebar_components import render_complete_sidebar
from utils.details_panel import render_details_panel

st.set_page_config(page_title="AgroVista - Terrain Management", layout="wide")

st.title("🗺️ Terrains Management")

# Initialize session state for selected items
if 'selected_terrain' not in st.session_state:
    st.session_state.selected_terrain = None
if 'selected_parcel' not in st.session_state:
    st.session_state.selected_parcel = None

# --- Load data from backend ---
df_activities, parcels_df, terrains_df, parcel_ids = load_data()

# Convert dataframes to lists for easier handling
terrains = terrains_df.to_dict('records') if not terrains_df.empty else []
all_parcels = parcels_df.to_dict('records') if not parcels_df.empty else []

# Evaluate parcel statuses
statuses = evaluate_parcel_status(df_activities) if not df_activities.empty else {}

# --- SIDEBAR ---
render_complete_sidebar(statuses)

# --- MAIN CONTENT AREA ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Interactive Map")
    
    # Create and populate map
    m = create_base_map()
    add_terrain_polygons(m, terrains_df, st.session_state.selected_terrain)
    add_parcel_polygons_and_markers(m, parcels_df, statuses, convert_status_to_display, st.session_state.selected_parcel)
    
    # Display map
    map_data = st_folium(
        m, 
        width=None, 
        height=500, 
        returned_objects=["last_object_clicked", "last_clicked"],
        key="terrain_map"
    )
    
    # Handle click events
    click_result = process_map_click(map_data, terrains, all_parcels)
    if click_result['type'] == 'parcel':
        st.session_state.selected_parcel = click_result['id']
        st.session_state.selected_terrain = click_result['terrain_id']
    elif click_result['type'] == 'terrain':
        st.session_state.selected_terrain = click_result['id']
        st.session_state.selected_parcel = None

    # Legend below map
    st.subheader("Legend")
    leg_col1, leg_col2 = st.columns(2)
    
    with leg_col1:
        st.write("**Terrain Colors:**")
        for color in ['🟢 Green', '🔵 Blue', '🟠 Orange', '🟣 Purple']:
            st.write(f"{color}")

# --- RIGHT PANEL: Details ---
with col2:
    render_details_panel(
        st.session_state.selected_terrain, 
        st.session_state.selected_parcel,
        terrains, 
        all_parcels, 
        statuses, 
        df_activities
    )