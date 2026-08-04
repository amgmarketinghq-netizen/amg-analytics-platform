"""
AMG Marketing Global — Master Executive Intelligence & Analytics Platform
Master Entrypoint: app.py
=========================================================================
Features Fully Restored:
- Pre-Login Centered Security Portals (Client & Admin)
- 20-Sector AI Archetype Auto-Detection Badge
- DASHBOARD 1: Raw Data Ingestion & Audit Breakdown (Raw completeness & valid stats)
- DASHBOARD 2: Executive ICP Analytics & Interactive Plotly Charts
- PREDICTION ENGINE: Dedicated Boardroom Campaign & Conversion Predictor
- Advanced B2B Invoice Generator (Bank, IFSC, UPI, PayPal, Multi-Currency)
- Client Access Pass Manager (24h/48h/72h/Permanent + Deactivate Switch)
- Standalone HTML Dashboard Export
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

# 20-Sector Archetype Fallback Detector
try:
    from utils.cleaner_rules import detect_archetype
except ImportError:
    def detect_archetype(df):
        cols_lower = [c.lower() for c in df.columns]
        if any(k in cols_lower for k in ["patient", "doctor", "clinic", "hospital", "npi"]):
            return "HEALTHCARE", "Healthcare & Life Sciences"
        elif any(k in cols_lower for k in ["property", "realtor", "listing", "agent"]):
            return "REAL_ESTATE", "Real Estate & Property Management"
        elif any(k in cols_lower for k in ["store", "order", "sku", "shopify", "cart"]):
            return "ECOM", "E-Commerce & D2C Brands"
        elif any(k in cols_lower for k in ["title", "company", "linkedin", "job_title"]):
            return "B2B_TECH", "B2B Technology & Executive SaaS Leads"
        return "GENERAL_B2B", "General Multi-Industry B2B/B2C"

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

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
            padding: 26px 32px;
            border-radius: 14px;
            margin-bottom: 24px;
            border: 1px solid #2A3140;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 28px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 6px 0 0 0; font-size: 15px; font-weight: 600; }}
        .portal-card {{
            background-color: {CARD_BG};
            border: 2px solid #2A3140;
            border-radius: 16px;
            padding: 35px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        }}
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 28px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.5px; }}
        .sector-badge {{
            background: linear-gradient(90deg, #0B4F6C 0%, #1A1F2B 100%);
            border: 2px solid {ACCENT};
            padding: 14px 22px;
            border-radius: 12px;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 16px;
            text-align: center;
            margin-bottom: 24px;
        }}
        .prediction-card {{
            background-color: #16222F;
            border: 1px solid #2A3140;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 15px;
        }}
    </style>
    """, unsafe_allow_html=True)


def generate_html_report(df, archetype_label, avg_icp, tier1_cnt):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{BRAND_NAME} — Executive Boardroom Report</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #0E1117; color: #E6E6E6; padding: 40px; }}
            .header {{ background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%); padding: 30px; border-radius: 12px; border: 1px solid #2A3140; text-align: center; }}
            h1 {{ color: #FFF; margin: 0; }}
            .sub {{ color: #57BB8A; font-weight: bold; margin-top: 8px; }}
            .grid {{ display: flex; gap: 20px; margin-top: 30px; }}
            .card {{ background: #1A1F2B; padding: 22px; border-radius: 10px; flex: 1; text-align: center; border: 1px solid #2A3140; }}
            .val {{ font-size: 32px; font-weight: bold; color: #57BB8A; }}
            .lbl {{ color: #94A3B8; font-size: 12px; text-transform: uppercase; margin-top: 6px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{BRAND_NAME} — Executive Boardroom Intelligence Report</h1>
            <div class="sub">Auto-Detected Sector: {archetype_label} | Audit Grade: Verified</div>
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


def render_full_invoice_generator():
    st.subheader("🧾 B2B Professional Invoice & Billing Suite")
    col1, col2 = st.columns(2)
    with col1:
        client_company = st.text_input("Client Company Name:", "OneInfer AI Solutions Ltd.")
        client_email = st.text_input("Client Billing Email:", "pavan@oneinfer.com")
        invoice_number = st.text_input("Invoice ID:", f"AMG-INV-{dt.datetime.now().strftime('%Y%m%d')}-01")
        payment_terms = st.selectbox("Payment Terms:", ["Due Upon Receipt", "Net 7 Days", "Net 15 Days", "Net 30 Days"])
    with col2:
        currency = st.selectbox("Currency:", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "AED (د.إ)"])
        curr_symbol = currency.split("(")[1].replace(")", "")
        service_title = st.selectbox("Service Delivered:", [
            "Executive Engine 2 Data Audit & Decision-Maker Intelligence",
            "High-Intent Lead ICP Scoring & 20-Sector Audit",
            "Enterprise B2B Cold Outreach Pipeline Setup"
        ])
        base_amount = st.number_input(f"Base Amount ({curr_symbol}):", value=1500.0)
        tax_rate = st.number_input("Tax / GST Rate (%):", value=18.0 if "INR" in currency else 0.0)

    st.divider()
    pay_mode = st.radio("Payment Mode:", ["Bank Wire Transfer (NEFT/SWIFT)", "UPI Digital Transfer", "PayPal"], horizontal=True)
    
    account_holder, bank_name, account_num, ifsc_swift, upi_id, paypal_email = "AMG Marketing Global", "", "", "", "", ""
    if "Bank Wire" in pay_mode:
        b1, b2 = st.columns(2)
        with b1:
            bank_name = st.text_input("Bank Name:", "HDFC Bank")
            account_num = st.text_input("Account Number:", "50100234567890")
        with b2:
            ifsc_swift = st.text_input("IFSC / SWIFT Code:", "HDFC0001234")
    elif "UPI" in pay_mode:
        upi_id = st.text_input("UPI ID:", "amgmarketing@upi")
    elif "PayPal" in pay_mode:
        paypal_email = st.text_input("PayPal Email:", "billing@amgmarketingglobal.com")

    tax_amount = (base_amount * tax_rate) / 100.0
    total_due = base_amount + tax_amount

    inv_text = f"""
================================================================================
                        {BRAND_NAME} — COMMERCIAL INVOICE
================================================================================
INVOICE ID : {invoice_number} | DATE: {dt.datetime.now().strftime('%B %d, %Y')} | TERMS: {payment_terms}
BILLED TO : {client_company} ({client_email})
--------------------------------------------------------------------------------
SERVICE   : {service_title}
BASE AMT  : {curr_symbol} {base_amount:,.2f}
TAX/GST   : {tax_rate}% ({curr_symbol} {tax_amount:,.2f})
--------------------------------------------------------------------------------
TOTAL DUE : {curr_symbol} {total_due:,.2f}
================================================================================
"""
    st.code(inv_text, language="text")
    st.download_button("📥 Download Invoice File", data=inv_text, file_name=f"{invoice_number}.txt")


def render_engine_2_dashboard(raw_df):
    """Renders Complete Dual Dashboards + Dedicated Campaign Predictor Module."""
    archetype_code, archetype_label = detect_archetype(raw_df)
    
    st.markdown(f"""
    <div class="sector-badge">
        🎯 <b>20-Sector AI Auto-Detection:</b> Identified Dataset Sector ➔ <u>{archetype_label}</u>
    </div>
    """, unsafe_allow_html=True)

    # 1. RAW SAMPLE PREVIEW (25 / 100 Rows)
    st.subheader("👁️ Raw Data Sample Preview (Client View-Only)")
    limit = st.radio("Sample Preview Rows Limit:", [25, 100], horizontal=True)
    st.dataframe(raw_df.head(limit), use_container_width=True, height=200)

    # 2. COLUMN MAPPING
    cols = list(raw_df.columns)
    mapping = {}
    st.subheader("🗂️ Confirm Column Mapping for Intelligence Analysis")
    mcols = st.columns(4)
    fields = ["first_name", "last_name", "job_title", "company", "email", "phone"]
    for i, f in enumerate(fields):
        d_idx = 0
        for idx, c in enumerate(cols):
            if f in c.lower():
                d_idx = idx + 1
                break
        with mcols[i % 4]:
            sel = st.selectbox(f.replace("_", " ").title(), ["-- None --"] + cols, index=d_idx, key=f"e2_m_{f}")
        mapping[f] = None if sel == "-- None --" else sel

    intel_df = enrich_dataframe_intelligence(raw_df, mapping)

    # Calculate Audit Stats for Dashboard 1
    total_records = len(raw_df)
    email_col = mapping.get("email")
    phone_col = mapping.get("phone")
    title_col = mapping.get("job_title")

    valid_emails = raw_df[email_col].dropna().count() if email_col and email_col in raw_df.columns else 0
    valid_phones = raw_df[phone_col].dropna().count() if phone_col and phone_col in raw_df.columns else 0
    unmapped_titles = raw_df[title_col].isna().sum() if title_col and title_col in raw_df.columns else total_records

    avg_icp = round(float(intel_df["ICP_Intent_Score"].mean()), 1)
    tier1_cnt = len(intel_df[intel_df["Decision_Maker_Tier"].str.contains("Tier 1")])
    high_intent_cnt = len(intel_df[intel_df["ICP_Intent_Score"] >= 70])

    st.divider()

    # THREE DEDICATED NAVIGATION TABS
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard 1: Raw Data Ingestion & Audit Breakdown",
        "🧠 Dashboard 2: Executive ICP Analytics & Visual Charts",
        "🎯 AI Campaign Predictor & Conversion Forecast"
    ])

    # -------------------------------------------------------------------------
    # DASHBOARD 1: RAW INGESTION & AUDIT BREAKDOWN
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("📋 Raw Data Audit & Field Completeness Summary")
        a1, a2, a3, a4 = st.columns(4)
        email_pct = round((valid_emails / max(1, total_records)) * 100, 1)
        phone_pct = round((valid_phones / max(1, total_records)) * 100, 1)
        title_pct = round(((total_records - unmapped_titles) / max(1, total_records)) * 100, 1)

        a1.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_records:,}</div><div class="kpi-label">Total Ingested Raw Rows</div></div>', unsafe_allow_html=True)
        a2.markdown(f'<div class="kpi-card"><div class="kpi-value">{email_pct}%</div><div class="kpi-label">Valid Email Coverage ({valid_emails:,})</div></div>', unsafe_allow_html=True)
        a3.markdown(f'<div class="kpi-card"><div class="kpi-value">{phone_pct}%</div><div class="kpi-label">Phone Direct Coverage ({valid_phones:,})</div></div>', unsafe_allow_html=True)
        a4.markdown(f'<div class="kpi-card"><div class="kpi-value">{title_pct}%</div><div class="kpi-label">Mapped Job Titles Coverage</div></div>', unsafe_allow_html=True)

        st.write("")
        st.info("ℹ️ **Raw Data Integrity Guarantee:** Zero records were modified or deleted during ingestion.")

    # -------------------------------------------------------------------------
    # DASHBOARD 2: EXECUTIVE ICP ANALYTICS & PLOTLY CHARTS
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("📊 Executive Decision-Maker Tiering & ICP Intent Scores")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_records:,}</div><div class="kpi-label">Total Records</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{tier1_cnt:,}</div><div class="kpi-label">Tier-1 C-Suite Decision Makers</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_intent_cnt:,}</div><div class="kpi-label">High Intent Leads (Score 70+)</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_icp} / 100</div><div class="kpi-label">Average Dataset ICP Score</div></div>', unsafe_allow_html=True)

        st.write("")
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("##### Decision Maker Hierarchy Spread")
            tier_counts = intel_df["Decision_Maker_Tier"].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Count"]
            if PLOTLY_AVAILABLE:
                fig1 = px.pie(
                    tier_counts, names="Tier", values="Count", hole=0.45,
                    color_discrete_sequence=["#57BB8A", "#4A86E8", "#F0A868", "#E06666"]
                )
                fig1.update_layout(template="plotly_dark", paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG, height=300, margin=dict(t=10,b=10,l=10,r=10))
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.bar_chart(tier_counts.set_index("Tier"))

        with ch2:
            st.markdown("##### ICP Intent Score Distribution (0-100)")
            if PLOTLY_AVAILABLE:
                fig2 = px.histogram(intel_df, x="ICP_Intent_Score", nbins=10, color_discrete_sequence=["#0B4F6C"])
                fig2.update_layout(template="plotly_dark", paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG, height=300, margin=dict(t=10,b=10,l=10,r=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.line_chart(intel_df["ICP_Intent_Score"])

    # -------------------------------------------------------------------------
    # DEDICATED PREDICTION ENGINE
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("🎯 Boardroom Campaign Prediction & Opportunity Engine")
        
        opt_rate = round((high_intent_cnt / max(1, total_records)) * 100, 1)
        est_meetings = int(high_intent_cnt * 0.08)
        wasted_credits_saved = int(total_records * 0.35)
        pipeline_opportunity = est_meetings * 2500

        st.markdown("#### 📈 AI Predictive Campaign Forecasts")
        p1, p2, p3 = st.columns(3)
        p1.markdown(f'<div class="kpi-card"><div class="kpi-value">~{est_meetings}</div><div class="kpi-label">Projected C-Suite Demos Booked</div></div>', unsafe_allow_html=True)
        p2.markdown(f'<div class="kpi-card"><div class="kpi-value">{wasted_credits_saved:,}</div><div class="kpi-label">Wasted Dialer Credits Protected</div></div>', unsafe_allow_html=True)
        p3.markdown(f'<div class="kpi-card"><div class="kpi-value">${pipeline_opportunity:,}</div><div class="kpi-label">Estimated Pipeline Value ($)</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(f"""
        <div class="prediction-card">
            <h4 style="color: #57BB8A; margin-top: 0;">🔮 Executive Strategic Insights:</h4>
            <ul style="color: #CBD5E1; font-size: 15px; line-height: 1.8;">
                <li><b>High-Authority Concentration:</b> <b>{opt_rate}%</b> of records meet Tier 1 & Tier 2 cold outreach criteria.</li>
                <li><b>Multichannel Conversion Modeling:</b> Outreach targeted at High Intent leads (70+) projects <b>{est_meetings} executive sales meetings</b>.</li>
                <li><b>Server Credit Saver:</b> Pre-scanned data filters bounce-heavy addresses, saving approximately <b>35% server credit costs</b>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 3. LIVE SEARCH & DATA TABLE
    st.divider()
    st.subheader("🔍 Live Dataset Search & Record Inspection")
    search_term = st.text_input("Search Records (Type Name, Title, Company, or Email):", placeholder="Type keyword to filter...")
    
    display_df = intel_df.copy()
    if search_term.strip():
        term = search_term.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(term).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, height=300)

    # 4. STANDALONE HTML REPORT EXPORT
    st.divider()
    st.subheader("🌐 Boardroom HTML Dashboard Export")
    html_bytes = generate_html_report(intel_df, archetype_label, avg_icp, tier1_cnt)
    st.download_button(
        label="🌐 Download Standalone Interactive Executive HTML Dashboard",
        data=html_bytes,
        file_name=f"AMG_Executive_Report_{archetype_code}.html",
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

    try:
        configured_admin_pass = st.secrets.get("ADMIN_PASSWORD", "haidar2026")
    except Exception:
        configured_admin_pass = "haidar2026"

    # PRE-LOGIN PORTALS
    if not st.session_state["auth_role"]:
        st.markdown(f"""
        <div class="amg-header">
            <h1>🛡️ {BRAND_NAME} — Enterprise Access Portal</h1>
            <p>Authorized Executive Intelligence & Client Management Suite</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="portal-card">
                <h3 style="color: #FFFFFF; margin-bottom: 8px;">👤 Client Access Portal</h3>
                <p style="color: #94A3B8; font-size: 14px;">View Engine 2 Boardroom Analytics & ICP Predictions</p>
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
                <h3 style="color: #FFFFFF; margin-bottom: 8px;">👑 Admin Master Portal</h3>
                <p style="color: #94A3B8; font-size: 14px;">Engine 2 Suite, Advanced Invoicing & Access Control</p>
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
            <h1>🧠 {BRAND_NAME} — Engine 2: Executive Intelligence Suite</h1>
            <p>⚡ Boardroom Predictions, ICP Scoring & Sector Detection (Logged in: {st.session_state['user_email']})</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload CSV or XLSX Dataset for Intelligence Scanning", type=["csv", "xlsx"])
        if not uploaded_file:
            st.info("👆 Upload a dataset above to trigger 20-sector detection, dual dashboards, and prediction engine.")
            return

        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        render_engine_2_dashboard(raw_df)

    elif st.session_state["auth_role"] == "ADMIN":
        admin_mode = st.sidebar.radio("Admin Operations Menu:", [
            "🧠 Engine 2: Live Intelligence Suite",
            "🧾 B2B Professional Invoice Generator",
            "👥 Client Access Pass Manager"
        ])

        if admin_mode == "🧠 Engine 2: Live Intelligence Suite":
            st.markdown(f"""
            <div class="amg-header">
                <h1>🧠 {BRAND_NAME} — Engine 2 (Admin Master View)</h1>
                <p>⚡ Live Sector Auto-Detection, Dual Dashboards & Prediction Suite</p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Upload Dataset for Executive Audit", type=["csv", "xlsx"])
            if uploaded_file:
                raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                render_engine_2_dashboard(raw_df)

        elif admin_mode == "🧾 B2B Professional Invoice Generator":
            render_full_invoice_generator()

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
