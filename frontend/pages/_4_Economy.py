import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.visualization import show_budget_vs_execution_parcel, show_budget_vs_execution_terrain, show_economic_reports, show_agricultural_simulations
from utils.api_client import get_api_client

st.set_page_config(page_title="AgroVista - Economy", layout="wide")
st.title("💰 Economic Management")

# Load data
activities_df, parcels_df, terrains_df, parcel_ids = load_data()
api_client = get_api_client()

tab1, tab2, tab3, tab4 = st.tabs(["Transactions", "Budget Analysis", "Reports", "Simulations"])

with tab1:
    st.subheader("💳 Transaction Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recent Transactions")
        try:
            transactions = api_client.get_transactions()
            if transactions:
                transactions_df = pd.DataFrame(transactions)
                st.dataframe(transactions_df.head(10), use_container_width=True)
            else:
                st.info("No transactions found.")
        except Exception as e:
            st.error(f"Error loading transactions: {e}")
    
    with col2:
        st.markdown("#### Budget Summary")
        try:
            budget = api_client.get_budget_summary()
            if budget:
                for key, value in budget.items():
                    if isinstance(value, (int, float)):
                        st.metric(key.replace('_', ' ').title(), f"${value:,.2f}")
            else:
                st.info("No budget summary available.")
        except Exception as e:
            st.error(f"Error loading budget summary: {e}")

with tab2:
    st.subheader("📊 Budget vs Execution Analysis")
    
    # Selector for analysis level
    analysis_level = st.radio("Analysis Level:", ["By Parcel", "By Terrain"], horizontal=True)
    
    if analysis_level == "By Parcel":
        if not parcels_df.empty:
            parcel_options = {row['name']: row['id'] for _, row in parcels_df.iterrows()}
            selected_parcel_name = st.selectbox("Select Parcel:", list(parcel_options.keys()))
            
            if selected_parcel_name:
                selected_parcel_id = parcel_options[selected_parcel_name]
                st.markdown(f"#### Budget Analysis for: {selected_parcel_name}")
                show_budget_vs_execution_parcel(selected_parcel_id)
        else:
            st.info("No parcels available for analysis.")
    
    elif analysis_level == "By Terrain":
        if not terrains_df.empty:
            terrain_options = {row['name']: row['id'] for _, row in terrains_df.iterrows()}
            selected_terrain_name = st.selectbox("Select Terrain:", list(terrain_options.keys()))
            
            if selected_terrain_name:
                selected_terrain_id = terrain_options[selected_terrain_name]
                
                # Get parcels for this terrain
                terrain_parcels = parcels_df[parcels_df['terrain_id'] == selected_terrain_id]
                if not terrain_parcels.empty:
                    terrain_parcel_ids = terrain_parcels['id'].tolist()
                    st.markdown(f"#### Budget Analysis for Terrain: {selected_terrain_name}")
                    show_budget_vs_execution_terrain(terrain_parcel_ids)
                else:
                    st.info(f"No parcels found for terrain: {selected_terrain_name}")
        else:
            st.info("No terrains available for analysis.")

with tab3:
    show_economic_reports()

with tab4:
    show_agricultural_simulations()
