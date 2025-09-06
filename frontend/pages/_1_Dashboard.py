import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000"  # Change if your backend is on a different host/port
st.title("AgroVista Dashboard")

# --- Safe function to get data ---
def safe_get(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Could not connect to {url}: {e}")
        return []

# --- 1. Get parcel data ---
parcels = safe_get(f"{BACKEND_URL}/parcels/")
df_parcels = pd.DataFrame(parcels)

# --- 2. Get indicators ---
indicators = safe_get(f"{BACKEND_URL}/control/indicators/")
df_indicators = pd.DataFrame(indicators)

# --- 3. Get transactions ---
transactions = safe_get(f"{BACKEND_URL}/economy/transactions/")
df_transactions = pd.DataFrame(transactions)

# --- KPIs: Parcels by status ---
# Flexible status mapping
status_map = {
    'active': 'optimal',
    'optimal': 'optimal',
    'attention': 'attention',
    'maintenance': 'critical',
    'critical': 'critical',
    # Spanish legacy mappings
    'activo': 'optimal',
    'óptimo': 'optimal',
    'atencion': 'attention',
    'atención': 'attention',
    'mantenimiento': 'critical',
    'critico': 'critical',
    'crítico': 'critical',
}
if not df_parcels.empty and 'status' in df_parcels:
    df_parcels['dashboard_status'] = df_parcels['status'].str.lower().map(status_map).fillna(df_parcels['status'])
    count = df_parcels['dashboard_status'].value_counts()
else:
    count = pd.Series({'optimal': 0, 'attention': 0, 'critical': 0})
col1, col2, col3 = st.columns(3)
col1.metric("In optimal state", count.get('optimal', 0))
col2.metric("Needs attention", count.get('attention', 0))
col3.metric("In critical state", count.get('critical', 0))

# --- KPI: Total accumulated production ---
prod_total = 0
if not df_indicators.empty:
    # Check for both English and Spanish production indicators
    prod_mask = df_indicators['name'].str.lower().str.contains('production|producción', na=False)
    prod_total = df_indicators[prod_mask]['value'].sum()
st.metric("Total accumulated production (kg)", f"{prod_total:,.0f}")

# --- KPIs: Total expenses and income ---
expenses = income = 0
if not df_transactions.empty and 'type' in df_transactions:
    # Check for both English and Spanish transaction types
    expenses = df_transactions[df_transactions['type'].isin(['expense', 'gasto'])]['amount'].sum()
    income = df_transactions[df_transactions['type'].isin(['income', 'ingreso'])]['amount'].sum()
col4, col5 = st.columns(2)
col4.metric("Total expenses", f"${expenses:,.0f}")
col5.metric("Total income", f"${income:,.0f}")

# --- Alerts ---
if not df_parcels.empty:
    critical = df_parcels[df_parcels['dashboard_status'] == 'critical']
    if not critical.empty:
        st.warning(f"⚠️ Parcels in critical state: {', '.join(critical['name'])}")
    else:
        st.success("No parcels in critical state.")

# --- Chart: Distribution of parcels by status ---
if not df_parcels.empty:
    status_dist = df_parcels['dashboard_status'].value_counts()
    st.subheader("Distribution of parcels by status")
    st.bar_chart(status_dist)

# --- Chart: Accumulated production by parcel ---
if not df_indicators.empty and not df_parcels.empty:
    # Check for both English and Spanish production indicators
    prod_mask = df_indicators['name'].str.lower().str.contains('production|producción', na=False)
    prod_parcel = df_indicators[prod_mask]
    if not prod_parcel.empty:
        # Merge with parcels to get parcel names, being explicit about column names
        prod_parcel = prod_parcel.merge(
            df_parcels[['id', 'name']].rename(columns={'name': 'parcel_name'}), 
            left_on='parcel_id', 
            right_on='id', 
            how='left'
        )
        # Group by parcel name and sum production values
        prod_summary = prod_parcel.groupby('parcel_name')['value'].sum().sort_values(ascending=False)
        st.subheader("Accumulated production by parcel (kg)")
        st.bar_chart(prod_summary)
    else:
        st.info("No production data available")
