"""
AMG Enterprise Analytics & Data Command Center
Module: modules/marketing_roi.py
===================================================================================
Marketing Campaign & Lead Acquisition ROI Dashboard Engine.
Pure Pandas/NumPy calculations for 100% exact numerical math.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def render_marketing_roi(df: pd.DataFrame, col_map: dict):
    """Renders marketing campaign ROI and performance analytics."""
    st.title("🎯 Marketing Campaign & Lead ROI Analytics")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload a Marketing or Campaign CSV file.")
        return

    # Sanitize Data & Compute Metrics
    cleaned_df = sanitize_dataframe(df, col_map)
    metrics = compute_quality_metrics(cleaned_df, col_map)

    num_col = col_map.get("num_col")
    cat_col = col_map.get("category_col")
    curr_sym = col_map.get("currency_symbol", "₹")

    total_ad_spend = 0.0
    avg_cpl = 0.0
    if num_col and num_col in cleaned_df.columns:
        numeric_series = pd.to_numeric(cleaned_df[num_col], errors="coerce").fillna(0.0)
        total_ad_spend = float(numeric_series.sum())
        avg_cpl = float(numeric_series.mean()) if len(cleaned_df) > 0 else 0.0

    # Key Metrics (Top Row)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Campaign Spend / Value", f"{curr_sym}{total_ad_spend:,.2f}")
    with c2:
        st.metric("Total Leads / Touchpoints", f"{metrics['n_rows']:,}")
    with c3:
        st.metric("Avg Cost Per Unit / Lead", f"{curr_sym}{avg_cpl:,.2f}")
    with c4:
        st.metric("Campaign Data Quality", f"{metrics['score']}%")

    st.markdown("---")

    # Visualizations
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Spend / Value by Channel / Campaign")
        if num_col and cat_col and cat_col in cleaned_df.columns:
            channel_spend = cleaned_df.groupby(cat_col)[num_col].sum().reset_index()
            fig_chan = px.bar(
                channel_spend, x=cat_col, y=num_col, color=cat_col,
                title=f"Spend Breakdown by {cat_col.title()}",
                text_auto=".2s"
            )
            fig_chan.update_layout(showlegend=False)
            st.plotly_chart(fig_chan, use_container_width=True)
        elif num_col and num_col in cleaned_df.columns:
            fig_spend_hist = px.histogram(
                cleaned_df, x=num_col,
                title="Campaign Cost Distribution",
                nbins=20, color_discrete_sequence=["#8b5cf6"]
            )
            st.plotly_chart(fig_spend_hist, use_container_width=True)
        else:
            st.info("No spend or conversion amount column detected for marketing analysis.")

    with col_b:
        st.subheader("🍩 Lead Acquisition Channel Share")
        if cat_col and cat_col in cleaned_df.columns:
            lead_counts = cleaned_df[cat_col].value_counts().reset_index()
            lead_counts.columns = [cat_col, "Leads"]
            fig_leads = px.pie(
                lead_counts, names=cat_col, values="Leads",
                title=f"Share by {cat_col.title()}",
                hole=0.45
            )
            st.plotly_chart(fig_leads, use_container_width=True)
        else:
            st.info("No campaign/channel column detected for acquisition breakdown.")

    st.markdown("---")
    st.subheader("📋 Cleaned Marketing Leads Master File")
    st.dataframe(cleaned_df.head(100), use_container_width=True)
