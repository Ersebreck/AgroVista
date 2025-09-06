"""
Details panel component utilities for DashMap
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from .status_utils import convert_status_to_display, get_status_emoji
import requests


def render_no_selection_message():
    """Render message when nothing is selected"""
    st.info("👆 Click on a terrain or parcel on the map to view details")


def render_parcel_details(parcel: Dict, statuses: Dict, df_activities: pd.DataFrame, terrains: List[Dict]):
    """Render detailed information for a selected parcel"""
    parcel_id = parcel.get('id')
    status_raw = statuses.get(parcel_id, ["Attention"])
    status_display = convert_status_to_display(status_raw)
    emoji = get_status_emoji(status_display)
    
    # Header with status emoji
    st.markdown(f"### {emoji} {parcel.get('name', 'Unnamed Parcel')}")
    st.write(f"**Type:** Parcel")
    st.write(f"**Status:** {status_display}")
    st.write(f"**ID:** {parcel_id}")
    st.write(f"**Current Use:** {parcel.get('current_use', 'Not specified')}")
    
    # Parent terrain info
    if parcel.get('terrain_id'):
        parent_terrain = next((t for t in terrains if t['id'] == parcel['terrain_id']), None)
        if parent_terrain:
            st.write(f"**Parent Terrain:** {parent_terrain.get('name', 'N/A')}")
    
    st.divider()
    
    # Activities section
    parcel_activities = df_activities[df_activities['parcel_id'] == parcel_id] if not df_activities.empty else None
    
    if parcel_activities is not None and not parcel_activities.empty:
        st.write(f"**📋 Activities ({len(parcel_activities)} total):**")
        
        # Show recent activities
        recent_activities = parcel_activities.tail(5)  # Last 5 activities
        for _, activity in recent_activities.iterrows():
            activity_date = activity.get('date', 'No date')
            activity_type = activity.get('type', 'Unknown')
            activity_desc = activity.get('description', '')
            
            if activity_desc and len(activity_desc) > 50:
                activity_desc = activity_desc[:47] + "..."
            
            st.write(f"• **{activity_type}** ({activity_date})")
            if activity_desc:
                st.write(f"  _{activity_desc}_")
    else:
        st.write("**📋 Activities:** No activities recorded")
    
    st.divider()


def render_terrain_details(terrain: Dict, parcels: List[Dict], statuses: Dict):
    """Render detailed information for a selected terrain"""
    st.markdown(f"### 🏞️ {terrain.get('name', 'Unnamed Terrain')}")
    st.write(f"**Type:** Terrain")
    st.write(f"**ID:** {terrain.get('id', 'N/A')}")
    st.write(f"**Description:** {terrain.get('description', 'No description available')}")
    
    # Get parcels in this terrain
    terrain_parcels = [p for p in parcels if p.get('terrain_id') == terrain['id']]
    st.write(f"**Parcels Count:** {len(terrain_parcels)}")
    
    if terrain_parcels:
        st.write("**📍 Parcels in this terrain:**")
        for parcel in terrain_parcels[:5]:  # Show first 5 parcels
            parcel_id = parcel.get('id')
            status_raw = statuses.get(parcel_id, ["Attention"])
            status_display = convert_status_to_display(status_raw)
            emoji = get_status_emoji(status_display)
            
            st.write(f"• {emoji} {parcel.get('name', 'Unnamed')} ({status_display})")
        
        if len(terrain_parcels) > 5:
            st.write(f"... and {len(terrain_parcels) - 5} more parcels")
    
    st.divider()


def render_quick_stats():
    """Render quick statistics section"""
    st.subheader("Quick Stats")
    
    # Try to get financial data using working utils functions
    try:
        response = requests.get("http://localhost:8000/economy/transactions/")
        if response.status_code == 200:
            transactions = response.json()
            total_expense = sum(t.get('amount', 0) for t in transactions if t.get('type') in ['expense', 'gasto'])
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('type') in ['income', 'ingreso'])
            st.metric("Total Expenses", f"${total_expense:,.0f}")
            st.metric("Total Income", f"${total_income:,.0f}")
        else:
            st.metric("Expenses", "N/A")
            st.metric("Income", "N/A")
    except:
        st.metric("Expenses", "N/A")
        st.metric("Income", "N/A")


def render_details_panel(selected_terrain_id: Optional[int], selected_parcel_id: Optional[int], 
                        terrains: List[Dict], parcels: List[Dict], statuses: Dict, 
                        df_activities: pd.DataFrame):
    """Render the complete details panel"""
    st.subheader("Details")
    
    # Show message if nothing selected
    if not selected_terrain_id and not selected_parcel_id:
        render_no_selection_message()
    
    # Show selected parcel details (prioritize parcel over terrain)
    elif selected_parcel_id:
        selected_parcel = next((p for p in parcels if p['id'] == selected_parcel_id), None)
        if selected_parcel:
            render_parcel_details(selected_parcel, statuses, df_activities, terrains)
    
    # Show selected terrain details (if no parcel selected)
    elif selected_terrain_id:
        selected_terrain = next((t for t in terrains if t['id'] == selected_terrain_id), None)
        if selected_terrain:
            render_terrain_details(selected_terrain, parcels, statuses)
    
    st.divider()
    render_quick_stats()