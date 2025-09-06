import streamlit as st

tab1, tab2, tab3 = st.tabs(["Transactions", "Reports", "Simulator"])

with tab1:
    st.write("Transaction consultation and registration.")

with tab2:
    st.write("Economic reports.")

with tab3:
    st.write("Scenario simulator.")
