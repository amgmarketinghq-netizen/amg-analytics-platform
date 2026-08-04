"""
AMG Marketing Global — Master Enterprise Analytics & Hygiene Platform
Master Entrypoint: app.py
=========================================================================
Integrated Utils:
- data_cleaner.py
- database.py
- invoice_generator.py
- narrative_engine.py
- tenant_theme.py
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

# SAFELY IMPORT ALL UTILS MODULES
try:
    from utils import data_cleaner, database, invoice_generator, narrative_engine, tenant_theme
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

# SAFELY IMPORT MODULES FOLDER
MODULES_STATUS = {}
for mod_name in ["boardroom_mode", "customer_behavior", "ecommerce_hub", "hr_analytics", 
                "marketing_roi", "sales_dashboard", "scenario_simulator", "time_intelligence"]:
    try:
        mod = __import__(f"modules.{mod_name}", fromlist=["*"])
        MODULES_STATUS[mod_name] = mod
    except ImportError:
        MODULES_STATUS[mod_name] = None

# Archetype Fallback Detector
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
        
        /* Modern Compact Centered Login Container */
        .login-box {{
            max-width: 420px;
            margin: 40px auto 20px auto;
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            text-align: center;
        }}
        
        .logo-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #0B4F6C 0%, #1A1F2B 100%);
            border: 1px solid {ACCENT};
            padding: 8px 16px;
            border-radius: 30px;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 14px;
            margin-bottom: 12px;
        }}

        .amg-header {{
            background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%);
            padding: 20px 26px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2A3140;
            text-align: center;
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 24px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 4px 0 0 0; font-size: 13px; font-weight: 600; }}
        
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 26px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; margin-top: 4px; }}
        
        .center-nav {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            padding: 10px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
    """, unsafe_allow_html=True)


def run_custom_module(mod_key, df):
    mod = MODULES_STATUS.get(mod_key)
    if not mod:
        return False
    for fn_name in ["render", "run", "main", "show_dashboard", "render_dashboard"]:
        if hasattr(mod, fn_name):
            try:
                fn = getattr(mod, fn_name)
                fn(df)
                return True
            except Exception:
                try:
                    fn()
                    return True
                except Exception:
                    pass
    return False


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
            "High-Intent Lead ICP Scoring & Multi-Sector Audit",
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


def render_master_executive_dashboard(raw_df):
    archetype_code, archetype_label = detect_archetype(raw_df)
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #0B4F6C 0%, #1A1F2B 100%); border: 1.5px solid {ACCENT}; padding: 12px 20px; border-radius: 10px; text-align: center; font-weight: 700; margin-bottom: 20px;">
        🎯 <b>20-Sector AI Auto-Detection:</b> Identified Dataset Sector ➔ <u>{archetype_label}</u>
    </div>
    """, unsafe_allow_html=True)

    selected_module = st.selectbox(
        "🎛️ Select Analysis Module to Run on Dataset:",
        [
            "👔 Boardroom Executive Mode (boardroom_mode)",
            "🎯 Customer Behavior & ICP Intelligence (customer_behavior)",
            "🛍️ E-Commerce Analytics Hub (ecommerce_hub)",
            "📈 Marketing ROI Engine (marketing_roi)",
            "💰 Sales Performance Dashboard (sales_dashboard)",
            "🔮 Scenario Simulator & Forecast (scenario_simulator)",
            "⏱️ Time Intelligence & Trends (time_intelligence)",
            "🏢 HR & Workforce Analytics (hr_analytics)"
        ]
    )

    st.divider()

    st.subheader("👁️ Raw Data Sample Preview (View-Only)")
    limit = st.radio("Sample Preview Rows Limit:", [25, 100], horizontal=True)
    st.dataframe(raw_df.head(limit), use_container_width=True, height=200)

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
            sel = st.selectbox(f.replace("_", " ").title(), ["-- None --"] + cols, index=d_idx, key=f"e2_m_{f}")
        mapping[f] = None if sel == "-- None --" else sel

    intel_df = enrich_dataframe_intelligence(raw_df, mapping)

    extracted_key = selected_module.split("(")[1].replace(")", "").strip()
    st.divider()
    
    executed = run_custom_module(extracted_key, intel_df)

    if not executed:
        c1, c2, c3, c4 = st.columns(4)
        avg_icp = round(float(intel_df["ICP_Intent_Score"].mean()), 1)
        tier1_cnt = len(intel_df[intel_df["Decision_Maker_Tier"].str.contains("Tier 1")])
        high_intent_cnt = len(intel_df[intel_df["ICP_Intent_Score"] >= 70])

        c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(intel_df):,}</div><div class="kpi-label">Total Ingested Leads</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{tier1_cnt:,}</div><div class="kpi-label">Tier-1 Decision Makers</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_intent_cnt:,}</div><div class="kpi-label">High Intent Leads</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_icp} / 100</div><div class="kpi-label">Avg ICP Score</div></div>', unsafe_allow_html=True)

        st.write("")
        st.dataframe(intel_df, use_container_width=True, height=300)


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

    # =========================================================================
    # SLEEK CENTERED VERTICAL LOGIN BOX (WITH ENTER-KEY SUBMIT)
    # =========================================================================
    if not st.session_state["auth_role"]:
        st.markdown("""
        <div class="login-box">
            <div class="logo-badge">🛡️ AMG ANALYTICS PLATFORM</div>
            <h2 style="color: #FFFFFF; margin: 5px 0 10px 0; font-weight: 800;">Sign In</h2>
            <p style="color: #94A3B8; font-size: 13px; margin-bottom: 20px;">
                Enter your authorized Email ID or Admin Key to unlock dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1.8, 1])
        
        with col_b:
            # CLIENT LOGIN FORM (PRESS ENTER TO SUBMIT)
            with st.form("client_login_form"):
                st.markdown("##### 👤 Client Email Access")
                c_email = st.text_input("Registered Email ID:", placeholder="client@company.com", label_visibility="collapsed")
                client_submit = st.form_submit_button("🚀 Enter Dashboard (Press Enter)", use_container_width=True)

                if client_submit:
                    is_valid, msg, rec = verify_client_email_access(c_email)
                    if is_valid:
                        st.session_state["auth_role"] = "CLIENT"
                        st.session_state["user_email"] = c_email
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.write("")

            # STACKED ADMIN LOGIN FORM
            with st.expander("👑 Admin Portal Access", expanded=False):
                with st.form("admin_login_form"):
                    a_pass = st.text_input("Admin Password:", type="password", placeholder="Enter Password")
                    admin_submit = st.form_submit_button("🔐 Admin Login", use_container_width=True)

                    if admin_submit:
                        if a_pass == configured_admin_pass:
                            st.session_state["auth_role"] = "ADMIN"
                            st.rerun()
                        else:
                            st.error("❌ Invalid Admin Password!")

        return

    # =========================================================================
    # LOGGED IN VIEW (CENTER NAVIGATION BAR)
    # =========================================================================
    st.markdown(f"""
    <div class="center-nav">
        <b>Role:</b> {st.session_state['auth_role']} | <b>Authorized Account:</b> {st.session_state['user_email'] if st.session_state['user_email'] else 'Master Admin'}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state["auth_role"] == "CLIENT":
        c_nav1, c_nav2 = st.columns([4, 1])
        with c_nav1:
            st.markdown(f"### 🧠 {BRAND_NAME} — Executive Analytics Dashboard")
        with c_nav2:
            if st.button("🚪 Logout"):
                st.session_state["auth_role"] = None
                st.session_state["user_email"] = ""
                st.rerun()

        uploaded_file = st.file_uploader("Upload CSV or XLSX Dataset for Intelligence Scanning", type=["csv", "xlsx"])
        if not uploaded_file:
            st.info("👆 Upload a dataset above to trigger 20-sector detection and custom analytics.")
            return

        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        render_master_executive_dashboard(raw_df)

    elif st.session_state["auth_role"] == "ADMIN":
        a_nav1, a_nav2 = st.columns([4, 1])
        with a_nav1:
            admin_mode = st.selectbox("🎛️ Admin Operations Suite:", [
                "🧠 Engine 2: Live Intelligence Suite",
                "🧾 B2B Professional Invoice Generator",
                "👥 Client Access Pass Manager"
            ])
        with a_nav2:
            st.write("")
            if st.button("🚪 Logout"):
                st.session_state["auth_role"] = None
                st.session_state["user_email"] = ""
                st.rerun()

        st.divider()

        if admin_mode == "🧠 Engine 2: Live Intelligence Suite":
            uploaded_file = st.file_uploader("Upload Dataset for Executive Audit", type=["csv", "xlsx"])
            if uploaded_file:
                raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                render_master_executive_dashboard(raw_df)

        elif admin_mode == "🧾 B2B Professional Invoice Generator":
            render_full_invoice_generator()

        elif admin_mode == "👥 Client Access Pass Manager":
            render_admin_client_manager()


if __name__ == "__main__":
    main()
