import streamlit as st

tab1, tab2 = st.tabs(["Activities", "Inventory"])

with tab1:
    st.write("Registration and consultation of agricultural activities.")

with tab2:
    st.write("Inventory management and consultation.")
