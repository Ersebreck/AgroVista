"""
Sidebar component utilities for DashMap
"""

import streamlit as st
from typing import Dict
from .parcel_status import summarize_parcel_status


def render_parcel_status_summary(statuses: Dict):
    """Render the parcel status summary in sidebar"""
    st.subheader("📈 Parcel Status")
    if statuses:
        summary = summarize_parcel_status(statuses)
        st.write(f"✅ Optimal: {summary['Optimal']}")
        st.write(f"⚠️ Attention: {summary['Attention']}")
        st.write(f"🚨 Critical: {summary['Critical']}")


def render_financial_summary():
    """Render financial summary in sidebar"""
    st.subheader("💰 Financial Summary")
    
    # Try to get financial data using API client
    try:
        from .api_client import get_api_client
        api_client = get_api_client()
        transactions = api_client.get_transactions()
        
        if transactions:
            total_expense = sum(t.get('amount', 0) for t in transactions if t.get('type') in ['expense', 'gasto'])
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('type') in ['income', 'ingreso'])
            st.metric("Total Expenses", f"${total_expense:,.0f}")
            st.metric("Total Income", f"${total_income:,.0f}")
            
            # Calculate net balance
            net_balance = total_income - total_expense
            balance_color = "normal" if net_balance >= 0 else "inverse"
            st.metric("Net Balance", f"${net_balance:,.0f}", delta_color=balance_color)
        else:
            st.info("No financial data available")
    except Exception:
        st.info("Financial data temporarily unavailable")


def render_complete_sidebar(statuses: Dict):
    """Render the complete sidebar with all components"""
    with st.sidebar:
        render_parcel_status_summary(statuses)
        st.divider()
        
        render_financial_summary()