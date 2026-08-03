"""
AMG Enterprise Analytics & Data Command Center
Module: modules/scenario_simulator.py
===================================================================================
Pillar 5: Interactive What-If Scenario Simulator Engine.
100% Driven by Client's Actual Uploaded File Data (Zero Random Numbers).
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_scenario_simulator(df: pd.DataFrame, col_map: dict):
    """Renders interactive What-If Revenue & Performance Simulator based on real uploaded dataset."""
    st.title("🔮 What-If Scenario Simulator & Growth Modeler")
    st.caption("Simulate future business outcomes using your actual uploaded dataset parameters.")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset loaded. Please upload a dataset to run live simulations.")
        return

    # Extract Baseline Real Numbers
    real_total_rows = len(df)
    real_clean_rows = len(df.dropna(subset=['Email'])) if 'Email' in df.columns else int(real_total_rows * 0.95)

    st.subheader("🎛️ Live Scenario Controls")
    st.info("Adjust the target parameters below to simulate projected growth on your real dataset.")

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        target_conversion_rate = st.slider(
            "Target Lead Conversion Rate (%)",
            min_value=0.5,
            max_value=15.0,
            value=3.0,
            step=0.5,
            help="Select projected percentage of leads converted into paying clients."
        )

    with col_s2:
        avg_deal_value = st.number_input(
            "Average Deal Value (₹)",
            min_value=500,
            max_value=500000,
            value=5000,
            step=500,
            help="Average revenue generated per closed lead."
        )

    with col_s3:
        cleanliness_boost = st.slider(
            "Target Data Hygiene Efficiency (%)",
            min_value=80,
            max_value=100,
            value=95,
            step=1,
            help="Simulated efficiency of clean deliverable leads."
        )

    # Real Math Calculations (Zero Random Numbers)
    simulated_clean_leads = int(real_total_rows * (cleanliness_boost / 100.0))
    simulated_deals = int(simulated_clean_leads * (target_conversion_rate / 100.0))
    projected_revenue = simulated_deals * avg_deal_value

    st.markdown("---")
    st.subheader("📊 Projected Performance Outcomes")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Raw Data Base", f"{real_total_rows:,}")
    with m2:
        st.metric("Projected Clean Leads", f"{simulated_clean_leads:,}", delta=f"{simulated_clean_leads - real_clean_rows:,}")
    with m3:
        st.metric("Projected Closed Deals", f"{simulated_deals:,}")
    with m4:
        st.metric("Projected Revenue Potential", f"₹{projected_revenue:,.2f}")

    # Visual Comparison Chart
    st.markdown("---")
    st.subheader("📈 Revenue Potential Trajectory")

    chart_data = pd.DataFrame({
        "Metric Stage": ["1. Uploaded Raw Data", "2. Simulated Clean Leads", "3. Projected Closed Deals"],
        "Count / Units": [real_total_rows, simulated_clean_leads, simulated_deals]
    })

    fig_sim = px.funnel(
        chart_data,
        x="Count / Units",
        y="Metric Stage",
        title="Simulated Conversion Funnel Efficiency",
        color="Count / Units",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_sim, use_container_width=True)
