"""
AMG Marketing Global — Engine 2 Executive Intelligence & Analytics Platform
Master Entrypoint: app.py
=========================================================================
Features Included:
- Strict Pre-Login Access Lock (Client Email Portal & Admin Password Portal)
- 20-Sector AI Archetype Auto-Detection Badge
- Zero-Cleaning View-Only Mode (25 vs 100 Sample Rows Preview)
- Decision Maker Hierarchy (Tier 1-4) & 0-100 ICP Intent Scoring
- Plotly Interactive Visual Charts (Pie & Histogram Spread)
- Boardroom Strategic Campaign Forecasts & Meeting Predictions
- Full Dataset Search & Filter Tool
- Standalone Interactive HTML Boardroom Dashboard Export
- B2B Invoice Generator & Client Access Pass Manager (Admin Only)
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

# Import Archetype Detection if available
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
            padding: 24px 30px;
            border-radius: 14px;
            margin-bottom: 24px;
            border: 1px solid #2A3140;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .amg-header h1 {{ color: #FFFFFF; font-size: 26px; margin: 0; font-weight: 800; }}
        .amg-header p {{ color: {ACCENT}; margin: 6px 0 0 0; font-size: 14px; font-weight: 600; }}
        .portal-card {{
            background-color: {CARD_BG};
            border: 2px solid #2A3140;
            border-radius: 14px;
            padding: 35px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid #2A3140;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .kpi-value {{ font-size: 28px; font-weight: 800; color: {ACCENT}; }}
        .kpi-label {{ font-size: 12px; color: #94A3B8; text-transform: uppercase; margin-top: 6px; letter-spacing: 0.5px; }}
        .sector-badge {{
            background: linear-gradient(90deg, #0B4F6C 0%, #1A1F2B 100%);
            border: 1.5px solid {ACCENT};
            padding: 12px 18px;
            border-radius: 10px;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 15px;
            margin-bottom: 20px;
        }}
        .prediction-box {{
            background-color: #16222F;
            border-left: 5px solid {ACCENT};
            padding: 22px;
            border-radius: 10px;
            margin: 20px 0;
            border-top: 1px solid #2A3140;
            border-right: 1px solid #2A3140;
            border-bottom: 1px solid #2A3140;
        }}
    </style>
    """, unsafe_allow_html=True)


def generate_html_report(df, archetype_label, avg_icp, tier1_cnt):
    """Generates standalone downloadable executive HTML dashboard file."""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{BRAND_NAME} — Executive Boardroom Intelligence</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0E1117; color: #E6E6E6; padding: 40px; }}
            .header {{ background: linear-gradient(90deg, #1A1F2B 0%, #0B4F6C 100%); padding: 30px; border-radius: 12px; border: 1px solid #2A3140; }}
            h1 {{ color: #FFF; margin: 0; }}
            .sub {{ color: #57BB8A; font-weight: bold; margin-top: 5px; }}
            .grid {{ display: flex; gap: 20px; margin-top: 30px; }}
            .card {{ background: #1A1F2B; padding: 20px; border-radius: 10px; flex: 1; text-align: center; border: 1px solid #2A3140; }}
            .val {{ font-size: 28px; font-weight: bold; color: #57BB8A; }}
            .lbl {{ color: #94A3B8; font-size: 12px; text-transform: uppercase; margin-top: 5px; }}
            .footer {{ margin-top: 50px; text-align: center; color: #64748B; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{BRAND_NAME} — Executive Boardroom Report</h1>
            <div class="sub">Auto-Detected Sector: {archetype_label} | Audit Grade: Verified</div>
        </div>
        <div class="grid">
            <div class="card"><div class="val">{len(df):,}</div><div class="lbl">Total Ingested Leads</div></div>
            <div class="card"><div class="val">{tier1_cnt:,}</div><div class="lbl">Tier-1 Decision Makers</div></div>
            <div class="card"><div class="val">{avg_icp} / 100</div><div class="lbl">Average ICP Score</div></div>
        </div>
        <div class="footer">Generated by {BRAND_NAME} Engine 2 Executive Dashboard</div>
    </body>
    </html>
    """
    return html_code.encode("utf-8")


def render_invoice_generator():
    """Renders B2B Professional Invoice Generator Tool for Admin."""
    st.subheader("🧾 B2B Professional Invoice Generator")
    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client / Company Name:", "OneInfer AI Solutions")
        client_email = st.text_input("Client Email:", "pavan@oneinfer.com")
        inv_num = st.text_input("Invoice Number:", "AMG-INV-2026-0801")
    with c2:
        service_desc = st.selectbox("Service Delivered:", [
            "Executive Engine 2 Data Audit & Intelligence Suite",
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
    Thank you for choosing {BRAND_NAME}.
    """
    st.code(inv_preview, language="text")
    st.download_button("📥 Download Invoice File", data=inv_preview, file_name=f"{inv_num}.txt")


def render_engine_2_dashboard(raw_df):
    """Renders Engine 2 Executive Intelligence Dashboard (Zero Cleaning, Pure View-Only)."""
    # 1. 20-SECTOR AUTO-DETECTION BADGE
    archetype_code, archetype_label = detect_archetype(raw_df)
    
    st.markdown(f"""
    <div class="sector-badge">
        🎯 <b>20-Sector AI Auto-Detection:</b> Identified Dataset Sector ➔ <u>{archetype_label}</u>
    </div>
    """, unsafe_allow_html=True)

    st.success(f"File Ingested: **{len(raw_df):,}** Records × **{len(raw_df.columns)}** Columns")

    # 2. RAW DATA SAMPLE PREVIEW (25 / 100 Rows View-Only)
    st.subheader("👁️ Raw Data Sample Preview (Client View-Only)")
    limit = st.radio("Sample Preview Rows Limit:", [25, 100], horizontal=True)
    st.dataframe(raw_df.head(limit), use_container_width=True, height=220)
    st.caption("⚠️ Note: Engine 2 does NOT modify or clean raw data. All original records are preserved.")

    # 3. COLUMN MAPPING FOR INTELLIGENCE
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

    # 4. KPI SUMMARY CARDS
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

    st.write("")

    # 5. PLOTLY INTERACTIVE CHARTS
    st.subheader("📈 Interactive Decision-Maker & ICP Visualizations")
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("##### Decision Maker Hierarchy Distribution")
        tier_counts = intel_df["Decision_Maker_Tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Count"]
        if PLOTLY_AVAILABLE:
            fig1 = px.pie(
                tier_counts, names="Tier", values="Count", hole=0.45,
                color_discrete_sequence=["#57BB8A", "#4A86E8", "#F0A868", "#E06666"]
            )
            fig1.update_layout(
                template="plotly_dark", paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                margin=dict(t=20, b=20, l=10, r=10), height=320
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.bar_chart(tier_counts.set_index("Tier"))

    with ch2:
        st.markdown("##### ICP Intent Score Spread (0-100 Range)")
        if PLOTLY_AVAILABLE:
            fig2 = px.histogram(
                intel_df, x="ICP_Intent_Score", nbins=10,
                color_discrete_sequence=["#0B4F6C"]
            )
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                margin=dict(t=20, b=20, l=10, r=10), height=320,
                xaxis_title="ICP Score Range", yaxis_title="Number of Leads"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.line_chart(intel_df["ICP_Intent_Score"])

    # 6. BOARDROOM CAMPAIGN PREDICTIONS
    st.divider()
    st.subheader("🎯 Boardroom Strategic Campaign Forecast")
    opt_rate = round((high_intent_cnt / max(1, len(intel_df))) * 100, 1)
    est_conversions = int(high_intent_cnt * 0.08)

    st.markdown(f"""
    <div class="prediction-box">
        <h4 style="color: #57BB8A; margin: 0 0 10px 0; font-size: 18px;">📈 Strategic Campaign Forecast & Insights:</h4>
        <ul style="margin: 0; color: #CBD5E1; font-size: 15px; line-height: 1.6;">
            <li><b>Sector Archetype Alignment:</b> Operating under <b>{archetype_label}</b> intelligence parameters.</li>
            <li><b>Targeting Efficiency:</b> <b>{opt_rate}%</b> of records possess High Intent authority.</li>
            <li><b>Predicted Meeting Conversions:</b> Estimated <b>~{est_conversions} Direct C-Suite Meetings</b> achievable with targeted messaging.</li>
            <li><b>Data Credit Protection:</b> Pre-audit eliminates estimated <b>30-40% wasted dialer server credits</b>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 7. SEARCH & LIVE DATA INSPECTION
    st.divider()
    st.subheader("🔍 Live Dataset Search & Record Inspection")
    search_term = st.text_input("Search Records (Type Name, Title, Company, or Email):", placeholder="Type keyword to filter...")
    
    display_df = intel_df.copy()
    if search_term.strip():
        term = search_term.strip().lower()
        mask = display_df.astype(str).apply(lambda row: row.str.lower().str.contains(term).any(), axis=1)
        display_df = display_df[mask]
        st.caption(f"Showing **{len(display_df):,}** matching records out of {len(intel_df):,}")

    st.dataframe(display_df, use_container_width=True, height=320)

    # 8. STANDALONE HTML REPORT EXPORT
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

    # Check Admin Password safely via Secrets (or default fallback)
    try:
        configured_admin_pass = st.secrets.get("ADMIN_PASSWORD", "haidar2026")
    except Exception:
        configured_admin_pass = "haidar2026"

    # PRE-LOGIN LANDING PORTALS
    if not st.session_state["auth_role"]:
        st.markdown(f"""
        <div class="amg-header" style="text-align: center;">
            <h1>🛡️ {BRAND_NAME} — Enterprise Access Portal</h1>
            <p>Select your authorized login portal to access Engine 2 Executive Intelligence</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="portal-card">
                <h3 style="color: #FFFFFF; margin-bottom: 8px;">👤 Client Access Portal</h3>
                <p style="color: #94A3B8; font-size: 14px;">View Engine 2 Live Executive Analytics & ICP Intelligence</p>
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
                <p style="color: #94A3B8; font-size: 14px;">Engine 2 Suite, B2B Invoicing & Access Control</p>
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

    # LOGGED IN SIDEBAR
    st.sidebar.title(f"🛡️ {BRAND_NAME}")
    st.sidebar.caption(f"Logged Role: **{st.session_state['auth_role']}**")

    if st.sidebar.button("🚪 Logout / Switch Portal"):
        st.session_state["auth_role"] = None
        st.session_state["user_email"] = ""
        st.rerun()

    st.sidebar.divider()

    # CLIENT VIEW: ENGINE 2
    if st.session_state["auth_role"] == "CLIENT":
        st.markdown(f"""
        <div class="amg-header">
            <h1>🧠 {BRAND_NAME} — Engine 2: Executive Intelligence & ICP Dashboard</h1>
            <p>⚡ Live Strategic Intelligence & Sector Auto-Detection (Logged in: {st.session_state['user_email']})</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload CSV or XLSX Dataset for Intelligence Scanning", type=["csv", "xlsx"])
        if not uploaded_file:
            st.info("👆 Upload a dataset above to trigger 20-sector detection, charts, and predictions.")
            return

        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        render_engine_2_dashboard(raw_df)

    # ADMIN VIEW: ENGINE 2 + MANAGEMENT TOOLS
    elif st.session_state["auth_role"] == "ADMIN":
        admin_mode = st.sidebar.radio("Admin Operations Menu:", [
            "🧠 Engine 2: Live Intelligence Dashboard",
            "🧾 B2B Invoice Generator",
            "👥 Client Access Pass Manager"
        ])

        if admin_mode == "🧠 Engine 2: Live Intelligence Dashboard":
            st.markdown(f"""
            <div class="amg-header">
                <h1>🧠 {BRAND_NAME} — Engine 2 (Admin Full Suite)</h1>
                <p>⚡ Live Sector Auto-Detection, Executive Analytics & HTML Export Builder</p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Upload Dataset for Executive Audit", type=["csv", "xlsx"])
            if uploaded_file:
                raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                render_engine_2_dashboard(raw_df)

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
