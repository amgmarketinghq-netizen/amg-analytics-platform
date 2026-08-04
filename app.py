"""
AMG Marketing Global — Unified Enterprise Analytics & Sanitation Platform
Master Entrypoint: app.py
"""

import sys
import os
import datetime as dt
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pass_guard import (
    verify_client_email_access, render_admin_client_manager
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
            padding: 22px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2A3140;
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 25px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 4px 0 0 0; font-size: 13px; font-weight: 600; }}
        .portal-card {{
            background-color: {CARD_BG};
            border: 2px solid #2A3140;
            border-radius: 14px;
            padding: 30px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 24px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; margin-top: 4px; }}
        .prediction-box {{
            background-color: #16222F;
            border-left: 4px solid #57BB8A;
            padding: 18px;
            border-radius: 8px;
            margin: 15px 0;
        }}
    </style>
    """, unsafe_allow_html=True)


def generate_html_report(df, avg_icp, tier1_cnt):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{BRAND_NAME} — Executive Boardroom Intelligence</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #0E1117; color: #E6E6E6; padding: 40px; }}
            .header {{ background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%); padding: 30px; border-radius: 12px; border: 1px solid #2A3140; }}
            h1 {{ color: #FFF; margin: 0; }}
            .sub {{ color: #57BB8A; font-weight: bold; margin-top: 5px; }}
            .grid {{ display: flex; gap: 20px; margin-top: 30px; }}
            .card {{ background: #1A1F2B; padding: 20px; border-radius: 10px; flex: 1; text-align: center; border: 1px solid #2A3140; }}
            .val {{ font-size: 28px; font-weight: bold; color: #57BB8A; }}
            .lbl {{ color: #94A3B8; font-size: 12px; text-transform: uppercase; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{BRAND_NAME} — Executive Intelligence Report</h1>
            <div class="sub">Executive Data Audit Grade: Verified</div>
        </div>
        <div class="grid">
            <div class="card"><div class="val">{len(df):,}</div><div class="lbl">Total Ingested Leads</div></div>
            <div class="card"><div class="val">{tier1_cnt:,}</div><div class="lbl">Tier-1 Decision Makers</div></div>
            <div class="card"><div class="val">{avg_icp} / 100</div><div class="lbl">Average ICP Score</div></div>
        </div>
    </body>
    </html>
    """
    return html_code.encode("utf-8")


def render_invoice_generator():
    st.subheader("🧾 B2B Professional Invoice Generator")
    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client / Company Name:", "OneInfer AI Solutions")
        client_email = st.text_input("Client Email:", "pavan@oneinfer.com")
        inv_num = st.text_input("Invoice Number:", "AMG-INV-2026-0801")
    with c2:
        service_desc = st.selectbox("Service Delivered:", [
            "Data Sanitation & Executive Audit (50,000 Leads)",
            "Executive ICP Intelligence & Decision-Maker Audit",
            "Monthly Data Pipeline Integration Retainer"
        ])
        amount = st.number_input("Invoice Amount ($ USD or ₹ INR):", value=1500)
        due_days = st.selectbox("Payment Terms:", ["Due Upon Receipt", "Net 15 Days", "Net 30 Days"])

    st.divider()
    inv_preview = f"""
    ========================================================================
    INVOICE: {inv_num} | ISSUER: {BRAND_NAME}
    BILLED TO: {client_name} ({client_email}) | DATE: {dt.datetime.now().strftime('%Y-%m-%d')}
    ========================================================================
    DESCRIPTION: {service_desc}
    TERMS: {due_days}
    TOTAL DUE: ${amount:,.2f}
    ========================================================================
    """
    st.code(inv_preview, language="text")
    st.download_button("📥 Download Invoice File", data=inv_preview, file_name=f"{inv_num}.txt")


def render_executive_analytics_view(raw_df, is_admin=False):
    st.success(f"Dataset Loaded: **{len(raw_df):,}** Records × **{len(raw_df.columns)}** Columns")

    st.subheader("👁️ Raw Data Sample Preview (View-Only)")
    limit = st.radio("Sample Preview Rows Limit:", [25, 100], horizontal=True)
    st.dataframe(raw_df.head(limit), use_container_width=True, height=220)

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
            sel = st.selectbox(f.replace("_", " ").title(), ["-- None --"] + cols, index=d_idx, key=f"e_m_{f}")
        mapping[f] = None if sel == "-- None --" else sel

    intel_df = enrich_dataframe_intelligence(raw_df, mapping)

    st.divider()
    st.subheader("📊 Executive Intelligence & ICP Analytics")
    c1, c2, c3, c4 = st.columns(4)
    avg_icp = round(float(intel_df["ICP_Intent_Score"].mean()), 1)
    tier1_cnt = len(intel_df[intel_df["Decision_Maker_Tier"].str.contains("Tier 1")])
    high_intent_cnt = len(intel_df[intel_df["ICP_Intent_Score"] >= 70])

    c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df):,}</div><div class="kpi-label">Total Ingested Leads</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{tier1_cnt:,}</div><div class="kpi-label">Tier-1 Decision Makers</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_intent_cnt:,}</div><div class="kpi-label">High Intent Leads (70+)</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_icp} / 100</div><div class="kpi-label">Avg ICP Intent Score</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🎯 Boardroom Strategic Campaign Forecast")
    opt_rate = round((high_intent_cnt / max(1, len(intel_df))) * 100, 1)
    est_conversions = int(high_intent_cnt * 0.08)

    st.markdown(f"""
    <div class="prediction-box">
        <h4 style="color: #57BB8A; margin: 0 0 8px 0;">📈 Strategic Campaign Forecast:</h4>
        <ul style="margin: 0; color: #CBD5E1; font-size: 14px;">
            <li><b>Targeting Efficiency:</b> <b>{opt_rate}%</b> of records possess High Intent authority.</li>
            <li><b>Predicted Meeting Conversions:</b> Estimated <b>~{est_conversions} Direct C-Suite Meetings</b>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("🔍 Live Dataset Search & Filter")
    search_term = st.text_input("Search Records:", placeholder="Type keyword to search...")
    display_df = intel_df.copy()
    if search_term.strip():
        term = search_term.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(term).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, height=300)

    st.divider()
    html_bytes = generate_html_report(intel_df, avg_icp, tier1_cnt)
    st.download_button(
        label="🌐 Download Executive Boardroom HTML Report",
        data=html_bytes,
        file_name="AMG_Executive_Report.html",
        mime="text/html",
        use_container_width=True
    )


def main():
    st.set_page_config(page_title="AMG Marketing Global Platform", page_icon="⚙️", layout="wide")
    inject_css()

    if "auth_role" not in st.session_state:
        st.session_state["auth_role"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = ""

    # Check Admin Password safely via Secrets (or fallback)
    try:
        configured_admin_pass = st.secrets.get("ADMIN_PASSWORD", "haidar2026")
    except Exception:
        configured_admin_pass = "haidar2026"

    if not st.session_state["auth_role"]:
        st.markdown(f"""
        <div class="amg-header" style="text-align: center;">
            <h1>🛡️ {BRAND_NAME} — Enterprise Access Portal</h1>
            <p>Select your authorized login access portal to proceed</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="portal-card">
                <h3 style="color: #FFFFFF; margin-bottom: 5px;">👤 Client Access Portal</h3>
                <p style="color: #94A3B8; font-size: 13px;">View Live Executive Analytics & ICP Intelligence</p>
            </div>
            """, unsafe_allow_html=True)
            c_email = st.text_input("Registered Email ID:", placeholder="client@company.com", key="c_in")
            if st.button("🚀 Unlock Client Dashboard", use_container_width=True):
                is_valid, msg, rec = verify_client_email_access(c_email)
                if is_valid:
                    st.session_state["auth_role"] = "CLIENT"
                    st.session_state["user_email"] = c_email
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        with col2:
            st.markdown("""
            <div class="portal-card">
                <h3 style="color: #FFFFFF; margin-bottom: 5px;">👑 Admin Master Portal</h3>
                <p style="color: #94A3B8; font-size: 13px;">Data Audit Suite, Invoicing & Access Control</p>
            </div>
            """, unsafe_allow_html=True)
            a_pass = st.text_input("Admin Password:", type="password", key="a_in")
            if st.button("🔐 Enter Admin Control Center", use_container_width=True):
                if a_pass == configured_admin_pass:
                    st.session_state["auth_role"] = "ADMIN"
                    st.rerun()
                else:
                    st.error("❌ Invalid Admin Password!")

        return

    st.sidebar.title(f"🛡️ {BRAND_NAME}")
    st.sidebar.caption(f"Role: **{st.session_state['auth_role']}**")

    if st.sidebar.button("🚪 Logout / Switch Portal"):
        st.session_state["auth_role"] = None
        st.session_state["user_email"] = ""
        st.rerun()

    st.sidebar.divider()

    if st.session_state["auth_role"] == "CLIENT":
        st.markdown(f"""
        <div class="amg-header">
            <h1>🧠 {BRAND_NAME} — Executive Analytics & ICP Dashboard</h1>
            <p>⚡ Live Strategic Intelligence (Logged in: {st.session_state['user_email']})</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload CSV/XLSX File for Live Intelligence Scanning", type=["csv", "xlsx"])
        if not uploaded_file:
            st.info("👆 Upload a dataset above to render executive charts and predictions.")
            return

        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        render_executive_analytics_view(raw_df, is_admin=False)

    elif st.session_state["auth_role"] == "ADMIN":
        admin_mode = st.sidebar.radio("Admin Control Suite:", [
            "🧠 Executive Analytics & Data Audit",
            "🧾 B2B Invoice Generator",
            "👥 Client Access Pass Manager"
        ])

        if admin_mode == "🧠 Executive Analytics & Data Audit":
            st.markdown(f"""
            <div class="amg-header">
                <h1>🧠 {BRAND_NAME} — Executive Analytics Suite</h1>
                <p>⚡ Strategic Intelligence & Live Search Filter</p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Upload Dataset to Audit", type=["csv", "xlsx"])
            if uploaded_file:
                raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                render_executive_analytics_view(raw_df, is_admin=True)

        elif admin_mode == "🧾 B2B Invoice Generator":
            render_invoice_generator()

        elif admin_mode == "👥 Client Access Pass Manager":
            st.markdown(f"""
            <div class="amg-header">
                <h1>👑 {BRAND_NAME} — Client Access Manager</h1>
                <p>Activate Client Emails, set 24h/48h/72h/Permanent passes, or toggle deactivation.</p>
            </div>
            """, unsafe_allow_html=True)
            render_admin_client_manager()


if __name__ == "__main__":
    main()
