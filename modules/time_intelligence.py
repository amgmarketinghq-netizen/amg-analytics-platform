"""
AMG Enterprise Analytics & Data Command Center
Module: modules/time_intelligence.py
===================================================================================
Pillar 4: Conditional Time-Intelligence & Cohort Analysis Engine.
STRICT RULE: Loads ONLY IF a Date / Timestamp column exists in the uploaded file.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def has_date_column(df: pd.DataFrame) -> str:
    """Checks if dataset contains any Date or Timestamp column."""
    if df is None or df.empty:
        return None
    
    date_keywords = ['date', 'time', 'created', 'timestamp', 'month', 'year', 'day']
    for col in df.columns:
        if any(kw in col.lower() for kw in date_keywords):
            return col
    return None


def render_time_intelligence(df: pd.DataFrame):
    """Renders MoM Growth & Time Trends Analysis."""
    date_col = has_date_column(df)
    
    if not date_col:
        st.warning("⚠️ No Date or Timestamp column detected in this dataset. Time-Intelligence module is deactivated for this upload.")
        return

    st.title("📅 Time-Intelligence & Growth Trends")
    st.caption(f"Analyzing time-series patterns using detected column: `{date_col}`")
    st.markdown("---")

    try:
        temp_df = df.copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors='coerce')
        temp_df = temp_df.dropna(subset=[date_col])

        # Aggregate by Month
        temp_df['YearMonth'] = temp_df[date_col].dt.to_period('M').astype(str)
        monthly_counts = temp_df['YearMonth'].value_counts().sort_index().reset_index()
        monthly_counts.columns = ['Period (Year-Month)', 'Record Volume']

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📈 Monthly Volume Trajectory")
            fig_trend = px.line(
                monthly_counts, 
                x='Period (Year-Month)', 
                y='Record Volume',
                markers=True,
                title="Period-over-Period Growth Curve",
                line_shape="spline"
            )
            fig_trend.update_traces(line_color="#0284c7", line_width=3)
            st.plotly_chart(fig_trend, use_container_width=True)

        with col2:
            st.subheader("📊 Period Breakdown")
            st.dataframe(monthly_counts, use_container_width=True)

    except Exception as e:
        st.error(f"Could not compute time intelligence: {e}")
