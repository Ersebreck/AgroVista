import streamlit as st
import pandas as pd
import requests
import altair as alt

API = "http://localhost:8000"

def show_simulations():
    st.title("🧪 Simulations")
    st.markdown("Explore saved projections and run new simulations.")

    # Show existing simulations
    try:
        res = requests.get(f"{API}/simulation/historical")
        res.raise_for_status()
        simulations = res.json()
    except Exception as e:
        st.error(f"Could not load simulations: {e}")
        return

    if not simulations:
        st.info("No saved simulations.")
    else:
        st.markdown("### 📋 Saved simulations")
        options = {f"{s['name']} ({s['creation_date']})": s for s in simulations}
        selection = st.selectbox("Select a scenario:", list(options.keys()))
        data = options[selection]
        df = pd.DataFrame.from_dict(data["results"], orient="index", columns=["Units"]).reset_index()
        df.rename(columns={"index": "Year"}, inplace=True)

        chart = alt.Chart(df).mark_line(point=True).encode(
            x="Year:O", y="Units:Q"
        ).properties(width=600, height=300)
        st.altair_chart(chart, use_container_width=True)

    # Create new simulation
    st.markdown("### ➕ New simulation")
    with st.form("simulation_form"):
        start_year = st.number_input("Start year", value=2025, step=1)
        years = st.slider("Years to simulate", 1, 10, 5)
        initial_units = st.number_input("Initial units", value=100)
        birth_rate = st.number_input("Birth rate (%)", value=20) / 100
        sale_rate = st.number_input("Sale rate (%)", value=10) / 100
        mortality_rate = st.number_input("Mortality rate (%)", value=5) / 100
        name = st.text_input("Scenario name", "Demo projection")
        submitted = st.form_submit_button("Simulate and save")

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
            res = requests.post(f"{API}/simulation/simulate", json=payload)
            res.raise_for_status()
            st.success("✅ Simulation saved.")
        except Exception as e:
            st.error(f"Error simulating: {e}")


# Legacy function for backward compatibility
def mostrar_simulaciones():
    """Legacy wrapper for show_simulations"""
    return show_simulations()
