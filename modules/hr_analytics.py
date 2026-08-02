"""
AMG Enterprise Analytics & Data Command Center
Module: modules/hr_analytics.py
===================================================================================
HR Workforce & Payroll Analytics Dashboard Engine.
Pure Pandas/NumPy calculations for 100% exact numerical math.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def render_hr_analytics(df: pd.DataFrame, col_map: dict):
    """Renders HR, Workforce, and Payroll Analytics Dashboard."""
    st.title("👥 HR Workforce & Payroll Analytics")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload an HR or Payroll CSV file.")
        return

    # Sanitize Data & Compute Metrics
    cleaned_df = sanitize_dataframe(df, col_map)
    metrics = compute_quality_metrics(cleaned_df, col_map)

    num_col = col_map.get("num_col")
    cat_col = col_map.get("category_col")
    curr_sym = col_map.get("currency_symbol", "₹")

    total_payroll = 0.0
    avg_salary = 0.0
    if num_col and num_col in cleaned_df.columns:
        numeric_series = pd.to_numeric(cleaned_df[num_col], errors="coerce").fillna(0.0)
        total_payroll = float(numeric_series.sum())
        avg_salary = float(numeric_series.mean()) if len(cleaned_df) > 0 else 0.0

    # Key Metrics (Top Row)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Workforce Headcount", f"{metrics['n_rows']:,}")
    with c2:
        st.metric("Total Payroll Dues", f"{curr_sym}{total_payroll:,.2f}")
    with c3:
        st.metric("Average Salary / Pay", f"{curr_sym}{avg_salary:,.2f}")
    with c4:
        st.metric("HR Data Integrity", f"{metrics['integrity']}%")

    st.markdown("---")

    # Visualizations
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Payroll Spend by Category/Dept")
        if num_col and cat_col and cat_col in cleaned_df.columns:
            dept_spend = cleaned_df.groupby(cat_col)[num_col].sum().reset_index()
            fig_dept = px.bar(
                dept_spend, x=cat_col, y=num_col, color=cat_col,
                title=f"Total Payroll by {cat_col.title()}",
                text_auto=".2s"
            )
            fig_dept.update_layout(showlegend=False)
            st.plotly_chart(fig_dept, use_container_width=True)
        elif num_col and num_col in cleaned_df.columns:
            fig_pay_hist = px.histogram(
                cleaned_df, x=num_col,
                title="Salary Distribution Curve",
                nbins=15, color_discrete_sequence=["#0d9488"]
            )
            st.plotly_chart(fig_pay_hist, use_container_width=True)
        else:
            st.info("No salary/compensation column detected for payroll breakdown.")

    with col_b:
        st.subheader("🍩 Department Headcount Distribution")
        if cat_col and cat_col in cleaned_df.columns:
            dept_counts = cleaned_df[cat_col].value_counts().reset_index()
            dept_counts.columns = [cat_col, "Headcount"]
            fig_headcount = px.pie(
                dept_counts, names=cat_col, values="Headcount",
                title=f"Headcount Share by {cat_col.title()}",
                hole=0.45
            )
            st.plotly_chart(fig_headcount, use_container_width=True)
        else:
            st.info("No department/role column detected for headcount distribution.")

    st.markdown("---")
    st.subheader("📋 Sanitized HR Workforce Records")
    st.dataframe(cleaned_df.head(100), use_container_width=True)
