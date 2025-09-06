"""
Visualization utilities for AgroVista frontend
"""

import streamlit as st
import altair as alt
import pandas as pd
from typing import List, Optional
from .api_client import get_api_client


def show_budget_vs_execution_terrain(parcel_ids: List[int]):
    """
    Show budget vs execution comparison for multiple parcels (terrain level).
    
    Args:
        parcel_ids: List of parcel IDs to analyze
    """
    api_client = get_api_client()
    year = pd.Timestamp.today().year
    all_data = []

    for parcel_id in parcel_ids:
        try:
            # Using working economy comparison endpoint
            result = api_client._make_request("GET", "/economy/comparison", 
                                            params={"year": year, "parcel_id": parcel_id})
            if result:
                all_data.extend(result)
        except Exception as e:
            st.warning(f"Error loading data for parcel {parcel_id}: {e}")

    if not all_data:
        st.warning("No economic data available for this terrain.")
        return

    df = pd.DataFrame(all_data)
    summary = df.groupby("category").agg({
        "budgeted_amount": "sum",
        "executed_amount": "sum",
    }).reset_index()
    summary["category"] = summary["category"].str.capitalize()

    chart = alt.Chart(summary).transform_fold(
        ["budgeted_amount", "executed_amount"],
        as_=["Type", "Amount"]
    ).mark_bar().encode(
        x=alt.X("category:N", title="Category"),
        y=alt.Y("Amount:Q", title="Total ($)"),
        color=alt.Color("Type:N", scale=alt.Scale(range=["#6666ff", "#76b900"])),
        tooltip=["category", "Amount", "Type"]
    ).properties(width=500, height=300)

    st.altair_chart(chart, use_container_width=True)


def show_budget_vs_execution_parcel(parcel_id: int):
    """
    Show budget vs execution comparison for a single parcel.
    
    Args:
        parcel_id: ID of the parcel to analyze
    """
    api_client = get_api_client()
    year = pd.Timestamp.today().year
    
    try:
        result = api_client._make_request("GET", "/economy/comparison", 
                                        params={"year": year, "parcel_id": parcel_id})
        if not result:
            st.warning("No economic data available for this parcel.")
            return
            
        df = pd.DataFrame(result)
        df["category"] = df["category"].str.capitalize()
        
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("executed_amount:Q", title="Executed Amount ($)"),
            color=alt.value("#76b900"),
            tooltip=["category", "budgeted_amount", "executed_amount", "difference"]
        ).properties(width=500, height=300).interactive()

        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.warning(f"Error loading economic comparison: {e}")


def show_terrain_kpis(terrain_df: pd.DataFrame, indicators_df: Optional[pd.DataFrame] = None):
    """
    Show KPIs for a terrain.
    
    Args:
        terrain_df: DataFrame with terrain activity data
        indicators_df: Optional DataFrame with indicator data
    """
    st.markdown("### 📊 KPIs")

    if not terrain_df.empty and "fecha" in terrain_df.columns:
        last_date = terrain_df["fecha"].max()
        days_inactive = (pd.Timestamp.today().normalize() - last_date).days

        st.metric("Last recorded activity", last_date.strftime("%d %b %Y"))
        st.metric("Average days without activity", round(days_inactive, 1))

    if indicators_df is not None and not indicators_df.empty:
        production_data = indicators_df[indicators_df["nombre"] == "Producción acumulada"]
        if not production_data.empty:
            total_production = production_data["valor"].sum()
            unit = production_data["unidad"].iloc[0]
            st.metric("Total estimated production", f"{round(total_production, 2)} {unit}")

    st.markdown("---")


def show_parcel_kpis(parcel_df: pd.DataFrame, indicators_df: Optional[pd.DataFrame] = None):
    """
    Show KPIs for a parcel.
    
    Args:
        parcel_df: DataFrame with parcel activity data
        indicators_df: Optional DataFrame with indicator data
    """
    st.markdown("### 📊 Key Indicators")

    if not parcel_df.empty and "fecha" in parcel_df.columns:
        last_date = parcel_df["fecha"].max()
        days_inactive = (pd.Timestamp.today().normalize() - last_date).days
        st.metric("Last activity", last_date.strftime("%d %b %Y"))
        st.metric("Days without activity", days_inactive)

    # Production (if available in indicators_df)
    if indicators_df is not None and not indicators_df.empty:
        production_data = indicators_df[indicators_df["nombre"] == "Producción acumulada"]
        if not production_data.empty:
            value = production_data.iloc[0]["valor"]
            unit = production_data.iloc[0]["unidad"]
            st.metric("Accumulated production", f"{value} {unit}")

    st.markdown("---")


def show_activity_frequency(parcel_df: pd.DataFrame):
    """
    Show activity frequency chart for a parcel.
    
    Args:
        parcel_df: DataFrame with parcel activity data
    """
    if not parcel_df.empty and "tipo" in parcel_df.columns:
        frequency = parcel_df["tipo"].value_counts()
        st.bar_chart(frequency)
    else:
        st.info("No activity data available for frequency analysis.")


def show_activity_details(parcel_df: pd.DataFrame, details_df: pd.DataFrame):
    """
    Show detailed activity visualization.
    
    Args:
        parcel_df: DataFrame with parcel activity data
        details_df: DataFrame with activity details
    """
    if parcel_df.empty or details_df.empty:
        st.warning("No detailed activity data available.")
        return

    # Merge activity and detail data
    merged_df = details_df.merge(
        parcel_df[["id", "nombre", "tipo", "fecha"]],
        left_on="actividad_id",
        right_on="id",
        suffixes=("_detail", "_activity")
    )
    
    # Convert values to numeric
    merged_df["numeric_value"] = pd.to_numeric(merged_df["valor"], errors="coerce")
    plot_df = merged_df[merged_df["numeric_value"].notnull()]
    
    if not plot_df.empty:
        chart = alt.Chart(plot_df).mark_bar().encode(
            x="nombre_detail:N",
            y="numeric_value:Q",
            color="tipo:N",
            tooltip=["nombre_detail", "tipo", "valor", "unidad", "fecha"]
        ).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No numeric details available for visualization.")


def show_latest_activities(parcel_df: pd.DataFrame):
    """
    Show latest activities for a parcel.
    
    Args:
        parcel_df: DataFrame with parcel activity data
    """
    if parcel_df.empty:
        st.info("No activity data available.")
        return

    if "fecha" not in parcel_df.columns:
        st.warning("No date information available for activities.")
        return

    latest_df = parcel_df.sort_values("fecha", ascending=False).head(5)
    st.dataframe(latest_df[["tipo", "fecha"]], use_container_width=True)
    
    if not latest_df.empty:
        st.metric("Last activity", latest_df["fecha"].max().strftime("%d %b"))


def show_economic_reports():
    """
    Show economic reports with filtering and export functionality.
    """
    st.subheader("📂 Economic Reports")
    st.markdown("Explore key metrics by terrain, parcel or category.")

    api_client = get_api_client()
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Year", [2025, 2024])
    with col2:
        category = st.text_input("Filter by category (optional)", "")

    try:
        # Using working economy comparison endpoint
        result = api_client._make_request("GET", "/economy/comparison", params={"year": year})
        if not result:
            st.info("No economic data available for the selected year.")
            return
            
        df = pd.DataFrame(result)
        
        # Apply category filter if specified
        if category and not df.empty:
            df = df[df["category"].str.contains(category, case=False, na=False)]

        if df.empty:
            st.info("No data matches the selected filters.")
            return

        # Display results
        st.markdown("### 📊 Comparative Summary")
        st.dataframe(df, use_container_width=True)

        # Export functionality
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV", 
            data=csv, 
            file_name=f"economic_report_{year}.csv", 
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Could not load economic data: {e}")


def show_agricultural_simulations():
    """
    Show agricultural simulations with creation and visualization functionality.
    """
    st.subheader("🧪 Agricultural Simulations")
    st.markdown("Explore saved projections and run new simulations.")

    api_client = get_api_client()

    # Show existing simulations
    try:
        simulations = api_client._make_request("GET", "/simulation/")
        
        if not simulations:
            st.info("No saved simulations.")
        else:
            st.markdown("#### 📋 Saved Simulations")
            options = {f"{s['name']} ({s['creation_date']})": s for s in simulations}
            selection = st.selectbox("Select a scenario:", list(options.keys()))
            
            if selection:
                data = options[selection]
                results_df = pd.DataFrame.from_dict(
                    data["results"], 
                    orient="index", 
                    columns=["Units"]
                ).reset_index()
                results_df.rename(columns={"index": "Year"}, inplace=True)

                # Create visualization
                chart = alt.Chart(results_df).mark_line(point=True).encode(
                    x=alt.X("Year:O", title="Year"),
                    y=alt.Y("Units:Q", title="Units")
                ).properties(width=600, height=300)
                st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"Could not load simulations: {e}")

    # Create new simulation
    st.markdown("#### ➕ Create New Simulation")
    with st.form("simulation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            start_year = st.number_input("Start year", value=2025, step=1)
            years = st.slider("Years to simulate", 1, 10, 5)
            initial_units = st.number_input("Initial units", value=100)
            
        with col2:
            birth_rate = st.number_input("Birth rate (%)", value=20.0) / 100
            sale_rate = st.number_input("Sale rate (%)", value=10.0) / 100
            mortality_rate = st.number_input("Mortality rate (%)", value=5.0) / 100
        
        name = st.text_input("Scenario name", "Agricultural projection")
        submitted = st.form_submit_button("🚀 Simulate and Save")

    if submitted:
        payload = {
            "start_year": start_year,
            "years": years,
            "initial_units": initial_units,
            "rates": {
                "birth_rate": birth_rate,
                "sale_rate": sale_rate,
                "mortality_rate": mortality_rate
            },
            "name": name,
            "save": True,
            "user_id": 1
        }
        
        try:
            result = api_client._make_request("POST", "/simulation/simulate", json=payload)
            if result:
                st.success("✅ Simulation created and saved successfully!")
                st.rerun()  # Refresh to show the new simulation
            else:
                st.error("Failed to create simulation.")
        except Exception as e:
            st.error(f"Error creating simulation: {e}")