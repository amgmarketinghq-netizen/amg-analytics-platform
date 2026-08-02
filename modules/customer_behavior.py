"""
AMG Enterprise Analytics & Data Command Center
Module: modules/customer_behavior.py
===================================================================================
Customer Behavior & Lead Sanitation Analytics Dashboard Engine.
Pure Pandas/NumPy calculations for 100% exact numerical math.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def render_customer_behavior(df: pd.DataFrame, col_map: dict):
    """Renders customer behavior and B2B lead sanitation analytics."""
    st.title("👥 Customer Behavior & Lead Quality Analytics")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload a Customer or Lead CSV file.")
        return

    # Sanitize Data & Compute Metrics
    cleaned_df = sanitize_dataframe(df, col_map)
    metrics = compute_quality_metrics(cleaned_df, col_map)

    # Key Metrics (Top Row)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Raw Records", f"{metrics['n_rows']:,}")
    with c2:
        st.metric("Clean Valid Records", f"{len(cleaned_df):,}")
    with c3:
        st.metric("Deliverability Index", f"{metrics['deliverability_index']}%")
    with c4:
        st.metric("Syntax Anomalies", f"{metrics['anomalies']:,}")

    st.markdown("---")

    # Visualizations
    col_a, col_b = st.columns(2)
    email_col = col_map.get("email")

    with col_a:
        st.subheader("📧 Email Domain Distribution")
        if email_col and email_col in cleaned_df.columns:
            domains = cleaned_df[email_col].dropna().astype(str).apply(
                lambda x: x.split("@")[-1].lower() if "@" in x else "invalid"
            )
            top_domains = domains.value_counts().head(10).reset_index()
            top_domains.columns = ["Domain", "Count"]

            fig_domain = px.bar(
                top_domains, x="Count", y="Domain", orientation="h",
                title="Top Lead Domains", color="Count",
                color_continuous_scale="Blues"
            )
            fig_domain.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
            st.plotly_chart(fig_domain, use_container_width=True)
        else:
            st.info("No email column mapped for domain analysis.")

    with col_b:
        st.subheader("🛡️ Data Health & Hygiene Breakdown")
        hygiene_data = pd.DataFrame({
            "Category": ["Valid Records", "Duplicate Rows", "Syntax Errors"],
            "Count": [len(cleaned_df), metrics["duplicates"], metrics["anomalies"]]
        })
        fig_hygiene = px.pie(
            hygiene_data, names="Category", values="Count",
            title="Data Health Distribution", hole=0.4,
            color_discrete_sequence=["#16a34a", "#eab308", "#ef4444"]
        )
        st.plotly_chart(fig_hygiene, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Verified Leads Master Preview")
    st.dataframe(cleaned_df.head(100), use_container_width=True)
