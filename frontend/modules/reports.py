import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

def show_reports():
    st.title("📂 Reports and Export")
    st.markdown("Explore key metrics by terrain, parcel or category.")

    year = st.selectbox("Year", [2025, 2024])
    category = st.text_input("Filter by category (optional)", "")

    try:
        res = requests.get(f"{API}/economy/comparison", params={"year": year})
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        st.error(f"Could not load information: {e}")
        return

    df = pd.DataFrame(data)
    if category:
        df = df[df["category"].str.contains(category, case=False)]

    st.markdown("### 📊 Comparative summary")
    st.dataframe(df)

    # Export to Excel
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name=f"report_{year}.csv", mime="text/csv")


# Legacy function for backward compatibility
def vista_reportes():
    """Legacy wrapper for show_reports"""
    return show_reports()
