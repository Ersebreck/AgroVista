"""
Sidebar component utilities for DashMap
"""

import streamlit as st
from typing import List, Dict
from temp_utils import summarize_parcel_status


def render_farm_overview(terrains: List[Dict], parcels: List[Dict], activities_count: int):
    """Render the farm overview section in sidebar"""
    st.subheader("🏞️ Farm Overview")
    st.metric("Total Terrains", len(terrains))
    st.metric("Total Parcels", len(parcels))
    st.metric("Total Activities", activities_count)


def render_parcel_status_summary(statuses: Dict):
    """Render the parcel status summary in sidebar"""
    st.subheader("📈 Parcel Status")
    if statuses:
        summary = summarize_parcel_status(statuses)
        st.write(f"🟢 Optimal: {summary['Optimal']}")
        st.write(f"🟡 Attention: {summary['Attention']}")
        st.write(f"🔴 Critical: {summary['Critical']}")


def render_usage_instructions():
    """Render usage instructions in sidebar"""
    st.subheader("💡 How to Use")
    st.write("**Click on any terrain or parcel** on the map to view detailed information.")
    st.write("• **Terrains** show as colored polygons")
    st.write("• **Parcels** have status emoji markers")
    st.write("• **Selected items** highlight in yellow")


def render_complete_sidebar(terrains: List[Dict], parcels: List[Dict], activities_count: int, statuses: Dict):
    """Render the complete sidebar with all components"""
    with st.sidebar:
        st.header("📊 Overview")
        
        render_farm_overview(terrains, parcels, activities_count)
        st.divider()
        
        render_parcel_status_summary(statuses)
        st.divider()
        
        render_usage_instructions()