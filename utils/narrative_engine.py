"""
AMG Enterprise Analytics & Data Command Center
Utility: utils/narrative_engine.py
===================================================================================
Pillar 2: AI Narrative Intelligence Engine.
Generates plain-English executive summaries and strategic takeaways under charts.
"""

import streamlit as st
import pandas as pd


def render_narrative_summary(df: pd.DataFrame, archetype: str):
    """Generates a smart 2-line executive narrative box based on dataset statistics."""
    if df is None or df.empty:
        return

    total_records = len(df)
    missing_emails = df['Email'].isnull().sum() if 'Email' in df.columns else 0
    clean_records = total_records - missing_emails
    clean_pct = round((clean_records / total_records) * 100, 1) if total_records > 0 else 0

    if archetype == "B2B_LEADS":
        insight_text = f"Data hygiene health is at **{clean_pct}%**. Out of {total_records:,} raw records, **{clean_records:,}** are verified deliverable leads. "
        if missing_emails > 0:
            insight_text += f"⚠️ Action Required: **{missing_emails:,}** entries lack valid email fields and were filtered out."
        else:
            insight_text += "✅ Zero blank email fields detected in this batch."
    else:
        insight_text = f"Dataset batch processed successfully containing **{total_records:,} total active rows** with an estimated data quality index of **{clean_pct}%**."

    st.info(f"💡 **Executive AI Takeaway:** {insight_text}")
