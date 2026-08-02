"""
AMG Enterprise Analytics & Data Command Center
Module: modules/ecommerce_hub.py
===================================================================================
E-Commerce & Retail Performance Analytics Dashboard Engine.
Pure Pandas/NumPy calculations for 100% exact numerical math.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def render_ecommerce_hub(df: pd.DataFrame, col_map: dict):
    """Renders E-Commerce sales, order fulfillment, and product performance analytics."""
    st.title("🛒 E-Commerce & Retail Performance Analytics")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload an E-Commerce or Orders CSV file.")
        return

    # Sanitize Data & Compute Metrics
    cleaned_df = sanitize_dataframe(df, col_map)
    metrics = compute_quality_metrics(cleaned_df, col_map)

    num_col = col_map.get("num_col")
    cat_col = col_map.get("category_col")
    curr_sym = col_map.get("currency_symbol", "₹")

    total_sales = 0.0
    avg_order_val = 0.0
    if num_col and num_col in cleaned_df.columns:
        numeric_series = pd.to_numeric(cleaned_df[num_col], errors="coerce").fillna(0.0)
        total_sales = float(numeric_series.sum())
        avg_order_val = float(numeric_series.mean()) if len(cleaned_df) > 0 else 0.0

    # Key Metrics (Top Row)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total GMV / Gross Revenue", f"{curr_sym}{total_sales:,.2f}")
    with c2:
        st.metric("Total Orders Processed", f"{metrics['n_rows']:,}")
    with c3:
        st.metric("Average Order Value (AOV)", f"{curr_sym}{avg_order_val:,.2f}")
    with c4:
        st.metric("Order Data Quality", f"{metrics['score']}%")

    st.markdown("---")

    # Visualizations
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📦 Revenue by Product Category / Region")
        if num_col and cat_col and cat_col in cleaned_df.columns:
            cat_sales = cleaned_df.groupby(cat_col)[num_col].sum().reset_index()
            fig_cat = px.bar(
                cat_sales, x=cat_col, y=num_col, color=cat_col,
                title=f"Total Sales by {cat_col.title()}",
                text_auto=".2s"
            )
            fig_cat.update_layout(showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        elif num_col and num_col in cleaned_df.columns:
            fig_order_hist = px.histogram(
                cleaned_df, x=num_col,
                title="Order Value Distribution",
                nbins=20, color_discrete_sequence=["#f59e0b"]
            )
            st.plotly_chart(fig_order_hist, use_container_width=True)
        else:
            st.info("No order amount column detected for revenue breakdown.")

    with col_b:
        st.subheader("🍩 Order Volume Distribution")
        if cat_col and cat_col in cleaned_df.columns:
            order_counts = cleaned_df[cat_col].value_counts().reset_index()
            order_counts.columns = [cat_col, "Orders"]
            fig_orders = px.pie(
                order_counts, names=cat_col, values="Orders",
                title=f"Order Volume Share by {cat_col.title()}",
                hole=0.45
            )
            st.plotly_chart(fig_orders, use_container_width=True)
        else:
            st.info("No category or status column detected for order distribution.")

    st.markdown("---")
    st.subheader("📋 Cleaned E-Commerce Order Records")
    st.dataframe(cleaned_df.head(100), use_container_width=True)
