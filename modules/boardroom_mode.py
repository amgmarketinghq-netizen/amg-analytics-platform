"""
AMG Enterprise Analytics & Data Command Center
Module: modules/boardroom_mode.py
===================================================================================
Pillar 3: Boardroom Presentation Mode Engine.
Minimalist, high-contrast, slide-style executive display mode for TV/Board meetings.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_boardroom_mode(df: pd.DataFrame, archetype: str):
    """Renders a full-screen boardroom presentation layout."""
    st.markdown("""
        <div style="background-color: #0f172a; padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
            <h1 style="color: #38bdf8; margin:0;">📺 Boardroom Presentation Mode</h1>
            <p style="color: #94a3b8; margin: 5px 0 0 0;">Executive Briefing Deck & Board-Ready Summary</p>
        </div>
    """, unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("⚠️ Please upload a dataset to generate Boardroom Deck.")
        return

    total_records = len(df)
    clean_leads = len(df.dropna(subset=['Email'])) if 'Email' in df.columns else total_records

    st.subheader("🎯 Key Boardroom KPIs")
    b1, b2, b3 = st.columns(3)
    
    with b1:
        st.metric("Total Batch Records", f"{total_records:,}")
    with b2:
        st.metric("Verified Deliverable Output", f"{clean_leads:,}")
    with b3:
        st.metric("Operational Efficiency Rate", f"{round((clean_leads/total_records)*100, 1) if total_records>0 else 100}%")

    st.markdown("---")
    st.subheader("📊 Boardroom Chart Briefing")
    
    if 'Email' in df.columns:
        domains = df['Email'].dropna().apply(lambda x: str(x).split('@')[-1].lower() if '@' in str(x) else 'Other')
        dom_counts = domains.value_counts().head(5).reset_index()
        dom_counts.columns = ['Domain', 'Lead Count']
        
        fig_board = px.pie(
            dom_counts, 
            names='Domain', 
            values='Lead Count', 
            title="Top 5 Market Domain Share",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Darkmint
        )
        st.plotly_chart(fig_board, use_container_width=True)
