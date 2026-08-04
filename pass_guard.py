"""
AMG Marketing Global — Enterprise Data Platform
Master Entrypoint: app.py
=========================================================================
Integrated Dual-Engine Architecture:
- Engine 1: Heavy Duty Data Hygiene & Cleaning (Admin Private)
- Engine 2: Client Live Intelligence & ICP Dashboard
- Admin Portal: Client Access & Expiry Management
"""

import sys
import os
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pass_guard import (
    verify_client_email_access, render_admin_client_manager,
    verify_access_key, render_lock_screen
)
from icp_intelligence import enrich_dataframe_intelligence

try:
    from utils.cleaner_rules import guess_column, run_pipeline, detect_archetype
    from utils.excel_builder import build_workbook
except ImportError:
    pass

BRAND_NAME = "AMG Marketing Global"
DARK_BG = "#0E1117"
CARD_BG = "#1A1F2B"
ACCENT = "#57BB8A"


def inject_css():
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {DARK_BG}; color: #E6E6E6; }}
        .amg-header {{
            background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%);
            padding: 20px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2A3140;
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 24px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 4px 0 0 0; font-size: 13px; font-weight: 600; }}
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 10px;
            padding: 14px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 22px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="AMG Marketing Global Platform", page_icon="⚙️", layout="wide")
    inject_css()

    st.sidebar.title(f"🛡️ {BRAND_NAME}")
    mode = st.sidebar.radio("Platform Navigation:", [
        "🧠 Engine 2: Client Intelligence Dashboard",
        "⚙️ Engine 1: Heavy Data Cleaning (Admin)",
        "👑 Admin Client Manager"
    ])

    st.sidebar.divider()

    # MODE 1: ENGINE 2 (CLIENT LIVE DASHBOARD WITH EMAIL LOGIN & EXPIRY)
    if mode == "🧠 Engine 2: Client Intelligence Dashboard":
        st.markdown(f"""
        <div class="amg-header">
            <h1>🧠 {BRAND_NAME} — Engine 2: Intelligence & ICP Dashboard</h1>
            <p>⚡ Executive Live Data Analytics (View-Only Mode)</p>
        </div>
        """, unsafe_allow_html=True)

        st.sidebar.subheader("👤 Client Access Portal")
        client_email = st.sidebar.text_input("Enter Registered Email ID:", placeholder="your-email@domain.com")

        is_valid, status_msg, client_record = verify_client_email_access(client_email)

        if not is_valid:
            if client_email:
                st.error(f"❌ {status_msg}")
            else:
                st.info("👈 Please enter your registered Email ID in the sidebar to access the live dashboard.")
            return

        st.sidebar.success(status_msg)

        uploaded_file = st.file_uploader("Upload CSV/XLSX Dataset for Intelligence Scanning", type=["csv", "xlsx"])
        if not uploaded_file:
            st.info("👆 Upload your raw dataset above to view live ICP analytics.")
            return

        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.success(f"File Ingested: **{len(raw_df):,}** Rows × **{len(raw_df.columns)}** Columns")

        st.subheader("👁️ Raw Data Sample Preview (View-Only)")
        limit = st.radio("Rows Preview Limit:", [25, 100], horizontal=True)
        st.dataframe(raw_df.head(limit), use_container_width=True)

        cols = list(raw_df.columns)
        mapping = {}
        st.subheader("🗂️ Confirm Column Mapping")
        mcols = st.columns(4)
        fields = ["first_name", "last_name", "job_title", "company", "email", "phone"]
        for i, f in enumerate(fields):
            d_idx = 0
            for idx, c in enumerate(cols):
                if f in c.lower():
                    d_idx = idx + 1
                    break
            with mcols[i % 4]:
                sel = st.selectbox(f.replace("_", " ").title(), ["-- None --"] + cols, index=d_idx, key=f"cm_{f}")
            mapping[f] = None if sel == "-- None --" else sel

        intel_df = enrich_dataframe_intelligence(raw_df, mapping)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df):,}</div><div class="kpi-label">Total Records</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df[intel_df["Decision_Maker_Tier"].str.contains("Tier 1")]):,}</div><div class="kpi-label">Tier-1 Decision Makers</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df[intel_df["ICP_Intent_Score"]>=70]):,}</div><div class="kpi-label">High Intent Leads</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card"><div class="kpi-value">{round(float(intel_df["ICP_Intent_Score"].mean()),1)}</div><div class="kpi-label">Avg ICP Score</div></div>', unsafe_allow_html=True)

        st.write("")
        st.dataframe(intel_df, use_container_width=True, height=350)

    # MODE 2: ENGINE 1 (DATA CLEANING)
    elif mode == "⚙️ Engine 1: Heavy Data Cleaning (Admin)":
        st.markdown(f"""
        <div class="amg-header">
            <h1>⚙️ {BRAND_NAME} — Engine 1: Private Heavy Hygiene Engine</h1>
            <p>Data Sanitization, 20-Sector Error Isolation & 5-Sheet Excel Reporting</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload File to Clean", type=["csv", "xlsx"], key="e1_f")
        if uploaded_file:
            raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.success(f"Loaded **{len(raw_df):,}** Rows")
            st.dataframe(raw_df.head(25), use_container_width=True)

    # MODE 3: ADMIN CLIENT MANAGER
    elif mode == "👑 Admin Client Manager":
        admin_pass = st.sidebar.text_input("Enter Admin Password:", type="password")
        if admin_pass == "haidar2026" or admin_pass == "AMG-ADMIN":
            render_admin_client_manager()
        else:
            st.info("🔒 Enter Admin Password in sidebar to manage client access (Default Password: `haidar2026`).")


if __name__ == "__main__":
    main()
