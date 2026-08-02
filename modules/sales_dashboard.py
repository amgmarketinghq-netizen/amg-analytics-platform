"""
AMG Enterprise Analytics & Data Command Center
Module: modules/sales_dashboard.py
===================================================================================
Sales & Revenue Pipeline Analytics Dashboard Engine.
Pure Pandas/NumPy calculations for 100% exact numerical math.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def render_sales_dashboard(df: pd.DataFrame, col_map: dict):
    """Renders full sales & revenue analytics views."""
    st.title("📈 Sales & Revenue Analytics Command Center")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload a Sales or Revenue CSV file.")
        return

    # Sanitize Data & Compute Metrics
    cleaned_df = sanitize_dataframe(df, col_map)
    metrics = compute_quality_metrics(cleaned_df, col_map)

    # Key Performance Indicators (Top Row)
    c1, c2, c3, c4 = st.columns(4)
    
    num_col = col_map.get("num_col")
    curr_sym = col_map.get("currency_symbol", "₹")
    
    total_rev = 0.0
    avg_deal = 0.0
    if num_col and num_col in cleaned_df.columns:
        numeric_series = pd.to_numeric(cleaned_df[num_col], errors="coerce").fillna(0.0)
        total_rev = float(numeric_series.sum())
        avg_deal = float(numeric_series.mean()) if len(cleaned_df) > 0 else 0.0

    with c1:
        st.metric("Total Revenue", f"{curr_sym}{total_rev:,.2f}")
    with c2:
        st.metric("Total Transactions", f"{metrics['n_rows']:,}")
    with c3:
        st.metric("Average Deal Value", f"{curr_sym}{avg_deal:,.2f}")
    with c4:
        st.metric("Data Quality Score (DQI)", f"{metrics['score']}%")

    st.markdown("---")

    # Interactive Visualizations
    cat_col = col_map.get("category_col")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Revenue Distribution")
        if num_col and cat_col and cat_col in cleaned_df.columns:
            fig_bar = px.histogram(
                cleaned_df, x=cat_col, y=num_col, color=cat_col,
                title=f"Total Revenue by {cat_col.title()}",
                text_auto=".2s"
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        elif num_col and num_col in cleaned_df.columns:
            fig_hist = px.histogram(
                cleaned_df, x=num_col,
                title="Revenue Value Distribution",
                nbins=20,
                color_discrete_sequence=["#2563eb"]
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No numeric column detected for revenue distribution charts.")

    with col_b:
        st.subheader("🍩 Category / Stage Breakdown")
        if cat_col and cat_col in cleaned_df.columns:
            cat_counts = cleaned_df[cat_col].value_counts().reset_index()
            cat_counts.columns = [cat_col, "Count"]
            fig_pie = px.pie(
                cat_counts, names=cat_col, values="Count",
                title=f"Volume Share by {cat_col.title()}",
                hole=0.45
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No categorical column detected for pie chart breakdown.")

    st.markdown("---")
    st.subheader("📋 Sanitized Dataset Master Preview")
    st.dataframe(cleaned_df.head(100), use_container_width=True)
