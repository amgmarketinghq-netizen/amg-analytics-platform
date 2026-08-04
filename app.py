"""
AMG Marketing Global — Engine 2 Entrypoint
Main Application: engine2_app.py
=========================================================================
Live Executive Intelligence & ICP Analytics Dashboard (View Only, No Cleaning)
"""

import sys
import os
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pass_guard import verify_access_key, render_lock_screen
from icp_intelligence import enrich_dataframe_intelligence

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

BRAND_NAME = "AMG Marketing Global"
DARK_BG = "#0E1117"
CARD_BG = "#1A1F2B"
ACCENT = "#57BB8A"


def main():
    st.set_page_config(page_title="AMG Engine 2 | Intelligence Dashboard", page_icon="🧠", layout="wide")
    
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {DARK_BG}; color: #E6E6E6; }}
        .amg-header {{
            background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2A3140;
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 26px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 4px 0 0 0; font-size: 14px; font-weight: 600; }}
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 24px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="amg-header">
        <h1>🧠 {BRAND_NAME} — Engine 2: Live Intelligence & ICP Dashboard</h1>
        <p>⚡ Executive Data Analytics, Decision-Maker Tiering & ICP Scoring (View-Only Mode)</p>
    </div>
    """, unsafe_allow_html=True)

    # ACCESS PASS CONTROLLER
    with st.sidebar:
        st.header("🔑 Access Pass Controller")
        user_key = st.text_input("Enter Access Pass Key", type="password", help="Enter 24h / 48h / 72h or Permanent VIP Pass Key")
        
        is_valid, status_msg, pass_info = verify_access_key(user_key)

        if is_valid:
            st.success(f"✅ Access Granted: {status_msg}")
            st.caption(f"🎫 Pass Assigned To: **{pass_info['label']}**")
            st.caption(f"⏳ Pass Type: **{pass_info['type']}**")
        else:
            st.error(f"❌ {status_msg}")

        st.divider()
        st.caption(f"{BRAND_NAME} · Engine 2 Analytics")

    if not is_valid:
        render_lock_screen()
        return

    # UNLOCKED DASHBOARD
    st.subheader("📂 Step 1: Upload Raw Client Dataset")
    uploaded_file = st.file_uploader("Upload CSV or Excel File for Live Intelligence Scanning", type=["csv", "xlsx", "xls"])

    if not uploaded_file:
        st.info("👆 Upload a dataset file above to unlock live intelligence scanning.")
        return

    try:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not load file: {e}")
        return

    if raw_df.empty:
        st.warning("File is empty.")
        return

    st.success(f"File Loaded: **{len(raw_df):,}** Rows × **{len(raw_df.columns)}** Columns")

    # RAW DATA PREVIEW (25 / 100 Rows View-Only)
    st.subheader("👁️ Raw Data Sample Preview (Client View-Only)")
    preview_limit = st.radio("Select Sample Rows Preview Limit:", options=[25, 100], horizontal=True)
    st.dataframe(raw_df.head(preview_limit), use_container_width=True, height=260)

    # MAPPING
    cols = list(raw_df.columns)
    options = ["-- None --"] + cols
    mapping = {}
    map_cols = st.columns(4)
    fields = ["first_name", "last_name", "job_title", "company", "email", "phone", "city", "state"]

    for i, field in enumerate(fields):
        default_idx = 0
        for c_idx, col_name in enumerate(cols):
            if field in col_name.lower():
                default_idx = c_idx + 1
                break
        with map_cols[i % 4]:
            sel = st.selectbox(field.replace("_", " ").title(), options, index=default_idx, key=f"e2_map_{field}")
        mapping[field] = None if sel == "-- None --" else sel

    intel_df = enrich_dataframe_intelligence(raw_df, mapping)

    st.divider()
    st.subheader("📊 Executive Intelligence & ICP Analytics Preview")

    c1, c2, c3, c4 = st.columns(4)
    avg_icp = round(float(intel_df["ICP_Intent_Score"].mean()), 1)
    tier1_count = len(intel_df[intel_df["Decision_Maker_Tier"].str.contains("Tier 1")])
    high_intent_count = len(intel_df[intel_df["ICP_Intent_Score"] >= 70])

    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df):,}</div><div class="kpi-label">Total Ingested Records</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{tier1_count:,}</div><div class="kpi-label">Tier-1 Decision Makers</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_intent_count:,}</div><div class="kpi-label">High Intent Leads (70+)</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_icp} / 100</div><div class="kpi-label">Avg ICP Intent Score</div></div>', unsafe_allow_html=True)

    st.write("")
    st.subheader("📋 Enriched Intelligence Table (View-Only)")
    st.dataframe(intel_df, use_container_width=True, height=350)


if __name__ == "__main__":
    main()
