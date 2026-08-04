"""
AMG Enterprise Analytics & Data Command Center
Main Application Entrypoint: app.py (v2.5 Enterprise Edition - Main Screen Login)
===================================================================================
Integrated Multi-Dashboard SaaS Platform with Main Screen Authentication & 20-Sector AI Detection.
"""

import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="AMG Enterprise Analytics Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Utilities & Branding
from utils.tenant_theme import apply_tenant_theme
from utils.narrative_engine import render_narrative_summary
from utils.data_cleaner import detect_dataset_archetype, compute_quality_metrics, sanitize_dataframe
from utils.database import (
    init_db, add_client, toggle_client_status, is_client_active, 
    get_all_clients, log_audit_trail, get_audit_logs, clear_audit_logs
)
from utils.invoice_generator import generate_invoice_html

# Import Dashboard Modules & Pillars
from modules.sales_dashboard import render_sales_dashboard
from modules.customer_behavior import render_customer_behavior
from modules.hr_analytics import render_hr_analytics
from modules.ecommerce_hub import render_ecommerce_hub
from modules.marketing_roi import render_marketing_roi
from modules.scenario_simulator import render_scenario_simulator
from modules.time_intelligence import has_date_column, render_time_intelligence
from modules.boardroom_mode import render_boardroom_mode

# Initialize System
init_db()
apply_tenant_theme(agency_name="AMG Marketing Global", primary_hex="#0284c7")

# Secret Admin Passcode
ADMIN_PASSCODE = "amg2026"

# 20-Sector Archetype Human-Readable Mapping
SECTOR_MAP = {
    "SALES": "Sales Performance & Commercial Operations",
    "B2B_LEADS": "B2B Technology & Executive SaaS Leads",
    "HR_EMPLOYEE": "HR Workforce & Staffing Intelligence",
    "FINANCIAL_FINES": "Banking, Finance & Financial Transactions",
    "ECOM": "B2C E-Commerce & Dropshipping Analytics",
    "HEALTHCARE": "Healthcare & Patient Records",
    "REAL_ESTATE": "Real Estate & Property Listings",
    "MARKETING": "Digital Marketing & Paid Ad Performance"
}


def render_sector_badge(archetype_code):
    """Displays prominent 20-Sector AI Auto-Detection Banner."""
    sector_name = SECTOR_MAP.get(archetype_code, f"{archetype_code.replace('_', ' ').title()} Industry Sector")
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #0B4F6C 0%, #1A1F2B 100%); border: 2px solid #0284c7; padding: 14px 22px; border-radius: 12px; color: #FFFFFF; font-weight: 700; font-size: 16px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        🎯 <b>20-Sector AI Auto-Detection:</b> Identified Dataset Sector ➔ <u>{sector_name}</u>
    </div>
    """, unsafe_allow_html=True)


# Sidebar Header
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=60)
st.sidebar.title("AMG Command Center")
st.sidebar.caption("v2.5 Enterprise Edition")
st.sidebar.markdown("---")

# Role Switcher (RBAC)
portal_mode = st.sidebar.radio("Select Access Mode:", ["👤 Client Portal", "🔑 Admin Panel"])
st.sidebar.markdown("---")

# ==========================================
# MODE 1: CLIENT PORTAL (MAIN SCREEN AUTHENTICATION)
# ==========================================
if portal_mode == "👤 Client Portal":
    
    # Store client email in session state
    if "client_email" not in st.session_state:
        st.session_state["client_email"] = ""

    # MAIN SCREEN LOGIN BOX (IF NOT LOGGED IN)
    if not st.session_state["client_email"]:
        st.title("⚡ AMG Enterprise Data Infrastructure Platform")
        st.caption("Authorized Client Portal Access")
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔒 Client Access Verification")
            with st.form("main_client_login"):
                email_in = st.text_input("Enter Registered Email ID:", placeholder="client@company.com")
                submit_btn = st.form_submit_button("🚀 Enter Portal", use_container_width=True)

                if submit_btn and email_in.strip():
                    cleaned_in = email_in.strip().lower()
                    all_clients = get_all_clients()
                    rec = next((c for c in all_clients if c["email"].lower() == cleaned_in), None)

                    if not rec:
                        st.error(f"❌ Access Denied! Email `{email_in}` is not registered with AMG Marketing Global.")
                        st.info("Please contact AMG Billing to purchase access.")
                    elif rec["status"].lower() != "active":
                        st.warning(f"⚠️ Account Suspended! Portal access for `{email_in}` is currently INACTIVE.")
                        st.info("Please contact AMG Support to activate your access.")
                    else:
                        st.session_state["client_email"] = cleaned_in
                        st.rerun()
        st.stop()

    # IF LOGGED IN: FETCH RECORD
    cleaned_email = st.session_state["client_email"]
    all_clients = get_all_clients()
    client_record = next((c for c in all_clients if c["email"].lower() == cleaned_email), None)

    if not client_record or client_record["status"].lower() != "active":
        st.session_state["client_email"] = ""
        st.rerun()

    st.sidebar.success(f"✅ Welcome {client_record['client_name']}")
    if st.sidebar.button("🚪 Logout Client"):
        st.session_state["client_email"] = ""
        st.rerun()

    # File Upload Section for Client
    st.sidebar.subheader("📁 Upload Data Batch")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            detection_res = detect_dataset_archetype(df, file_name=uploaded_file.name)
            archetype = detection_res["archetype"]
            col_map = detection_res["mapping"]

            metrics = compute_quality_metrics(df, col_map)
            clean_df = sanitize_dataframe(df, col_map)
            
            # Log audit trail
            log_audit_trail(
                email=cleaned_email,
                file_name=uploaded_file.name,
                total_rows=len(df),
                clean_rows=len(clean_df),
                quality_score=metrics["score"]
            )

            # RENDER 20-SECTOR AI AUTO-DETECTION BADGE
            render_sector_badge(archetype)

            # Render Executive AI Takeaway Summary
            render_narrative_summary(df, archetype)

            # Check if Date Column Exists for Conditional Tab 4
            date_col_found = has_date_column(df)

            # Construct Dynamic Tabs List
            tabs_list = [
                "📊 Main Executive Analytics",
                "🔮 What-If Growth Simulator",
                "📺 Boardroom Mode"
            ]
            if date_col_found:
                tabs_list.append("📅 Time & Growth Intelligence")

            client_tabs = st.tabs(tabs_list)

            # TAB 1: MAIN DASHBOARD MODULE
            with client_tabs[0]:
                if archetype == "SALES":
                    render_sales_dashboard(df, col_map)
                elif archetype == "B2B_LEADS":
                    render_customer_behavior(df, col_map)
                elif archetype == "HR_EMPLOYEE":
                    render_hr_analytics(df, col_map)
                elif archetype == "FINANCIAL_FINES":
                    render_ecommerce_hub(df, col_map)
                else:
                    render_marketing_roi(df, col_map)

            # TAB 2: WHAT-IF SCENARIO SIMULATOR
            with client_tabs[1]:
                render_scenario_simulator(df, col_map)

            # TAB 3: BOARDROOM PRESENTATION MODE
            with client_tabs[2]:
                render_boardroom_mode(df, archetype)

            # TAB 4: CONDITIONAL TIME INTELLIGENCE (LOADS ONLY IF DATE EXISTS)
            if date_col_found and len(client_tabs) > 3:
                with client_tabs[3]:
                    render_time_intelligence(df)

        except Exception as e:
            st.error(f"Error processing dataset: {e}")
    else:
        st.title(f"👋 Welcome, {client_record['client_name']}!")
        st.write("Upload a CSV or Excel dataset in the sidebar to unlock executive analytics, what-if simulators, and boardroom reports.")


# ==========================================
# MODE 2: ADMIN PANEL (MAIN SCREEN PASSCODE AUTHENTICATION)
# ==========================================
else:
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    # MAIN SCREEN ADMIN LOGIN BOX (IF NOT AUTHENTICATED)
    if not st.session_state["admin_logged_in"]:
        st.title("🔒 AMG Admin Command Center")
        st.caption("Restricted Administrative Access")
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔑 Admin Passcode Authentication")
            with st.form("main_admin_login"):
                pass_in = st.text_input("Enter Admin Passcode:", type="password", placeholder="Enter Password")
                admin_btn = st.form_submit_button("🔐 Authenticate Admin", use_container_width=True)

                if admin_btn:
                    if pass_in == ADMIN_PASSCODE:
                        st.session_state["admin_logged_in"] = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid Admin Passcode!")
        st.stop()

    st.sidebar.success("✅ Admin Authenticated")
    if st.sidebar.button("🚪 Logout Admin"):
        st.session_state["admin_logged_in"] = False
        st.rerun()

    admin_menu = st.sidebar.radio(
        "Admin Navigation",
        [
            "📊 Test Live Analytics Engine",
            "👥 Manage Client Access",
            "📄 Generate HTML Invoice",
            "📜 View Audit Trail Logs"
        ]
    )

    # ADMIN FEATURE 1: TEST ANALYTICS
    if admin_menu == "📊 Test Live Analytics Engine":
        st.title("📊 Live Analytics Engine (Admin Preview)")
        uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            detection_res = detect_dataset_archetype(df, file_name=uploaded_file.name)
            archetype = detection_res["archetype"]
            col_map = detection_res["mapping"]

            # RENDER 20-SECTOR AI AUTO-DETECTION BADGE
            render_sector_badge(archetype)

            render_narrative_summary(df, archetype)

            if archetype == "SALES":
                render_sales_dashboard(df, col_map)
            elif archetype == "B2B_LEADS":
                render_customer_behavior(df, col_map)
            elif archetype == "HR_EMPLOYEE":
                render_hr_analytics(df, col_map)
            elif archetype == "FINANCIAL_FINES":
                render_ecommerce_hub(df, col_map)
            else:
                render_marketing_roi(df, col_map)

    # ADMIN FEATURE 2: MANAGE CLIENTS (TOGGLE ACTIVE / INACTIVE + SEARCH)
    elif admin_menu == "👥 Manage Client Access":
        st.title("👥 Client Portal Access & Toggle Control")
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("➕ Register New Client")
            c_name = st.text_input("Client Business Name")
            c_email = st.text_input("Client Email Address")
            c_status = st.selectbox("Initial Status", ["Active", "Inactive"])

            if st.button("Add Client Access"):
                if c_name and c_email:
                    if add_client(c_name, c_email, c_status):
                        st.success(f"Client '{c_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Client email already exists!")
                else:
                    st.warning("Please fill all fields.")

        with col2:
            st.subheader("⚙️ Active / Inactive Access Controls")
            search_query = st.text_input("🔍 Search Client by Name or Email:", placeholder="Type to search...").strip().lower()
            
            clients = get_all_clients()
            if clients:
                filtered_clients = [
                    c for c in clients 
                    if search_query in c['client_name'].lower() or search_query in c['email'].lower()
                ] if search_query else clients

                if filtered_clients:
                    for c in filtered_clients:
                        st.write(f"**{c['client_name']}** ({c['email']}) — Status: **{c['status']}**")
                        new_st = "Inactive" if c['status'] == "Active" else "Active"
                        if st.button(f"Set {new_st}", key=f"toggle_{c['client_id']}"):
                            toggle_client_status(c['email'], new_st)
                            st.rerun()
                        st.markdown("---")
                else:
                    st.info("No matching clients found.")
            else:
                st.info("No clients registered yet.")

    # ADMIN FEATURE 3: INVOICE GENERATOR (ENTERPRISE UPGRADE)
    elif admin_menu == "📄 Generate HTML Invoice":
        st.title("📄 Enterprise HTML Invoice Generator")
        st.caption("Generate minimal, high-converting invoices tailored for International or Domestic clients.")
        st.markdown("---")

        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.subheader("📋 Invoice & Client Details")
            inv_id = st.text_input("Invoice ID", value="INV-2026-001")
            client_n = st.text_input("Client Name", placeholder="HLM Contact Center")
            client_e = st.text_input("Client Email", placeholder="suvaisha@hlm.com")
            curr = st.selectbox("Currency Symbol", ["₹", "$", "€", "£", "AED"])
            pay_terms = st.selectbox("Payment Terms", ["Due Upon Receipt", "Net 7 Days", "Net 15 Days", "Net 30 Days"])

            st.markdown("---")
            st.subheader("💼 Service Details")
            service_desc = st.text_input(
                "Service Description", 
                value="AMG Enterprise Data Infrastructure & Analytics Suite"
            )
            service_amt = st.number_input("Service Amount", value=1500.0, step=100.0)
            disc_pct = st.number_input("Discount (%)", value=0.0)
            tax_pct = st.number_input("Tax Rate (%)", value=0.0)

            st.markdown("---")
            st.subheader("💳 Payment Methods To Include")
            
            selected_pay_methods = st.multiselect(
                "Select Allowed Payment Options:",
                ["PayPal", "Bank Transfer", "UPI"],
                default=["Bank Transfer"]
            )

            paypal_email = ""
            bank_info = {}
            upi_info = {}

            if "PayPal" in selected_pay_methods:
                st.markdown("**🌐 PayPal Settings:**")
                paypal_email = st.text_input("PayPal Email Address", value="payments@amgmarketing.global")

            if "Bank Transfer" in selected_pay_methods:
                st.markdown("**🏛️ Bank Transfer Settings:**")
                b_name = st.text_input("Bank Name", value="HDFC Bank")
                b_acc_name = st.text_input("Account Holder Name", value="AMG Marketing Global")
                b_acc_no = st.text_input("Account No / IBAN", value="502000XXXXXX")
                b_swift = st.text_input("IFSC / SWIFT Code", value="HDFC0001234")
                bank_info = {
                    "bank_name": b_name,
                    "account_name": b_acc_name,
                    "account_no": b_acc_no,
                    "swift_ifsc": b_swift
                }

            if "UPI" in selected_pay_methods:
                st.markdown("**⚡ UPI Settings:**")
                upi_id = st.text_input("UPI ID", value="amgmarketing@upi")
                upi_payee = st.text_input("Payee Name", value="AMG Marketing Global")
                upi_info = {"upi_id": upi_id, "payee_name": upi_payee}

        with col_b:
            st.subheader("👁️ Live Invoice Preview")
            items = [{"description": service_desc, "amount": service_amt}]
            
            html_out = generate_invoice_html(
                inv_id=inv_id,
                client_name=client_n,
                client_email=client_e,
                items=items,
                currency=curr,
                tax_pct=tax_pct,
                disc_pct=disc_pct,
                payment_terms=pay_terms,
                payment_methods=selected_pay_methods,
                bank_details=bank_info if "Bank Transfer" in selected_pay_methods else None,
                paypal_email=paypal_email if "PayPal" in selected_pay_methods else "",
                upi_details=upi_info if "UPI" in selected_pay_methods else None,
                agency_name="AMG Marketing Global"
            )
            
            st.components.v1.html(html_out, height=650, scrolling=True)

            st.download_button(
                label="📥 Download HTML Invoice",
                data=html_out,
                file_name=f"Invoice_{inv_id}_{client_n.replace(' ', '_')}.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )

    # ADMIN FEATURE 4: AUDIT LOGS (WITH CLEAR LOGS CAPABILITY)
    elif admin_menu == "📜 View Audit Trail Logs":
        st.title("📜 System Audit & Client Usage Logs")
        st.markdown("---")

        logs = get_audit_logs()
        if logs:
            col_l1, col_l2 = st.columns([3, 1])
            with col_l1:
                st.write(f"Total Logged Actions: **{len(logs)}**")
            with col_l2:
                if st.button("🗑️ Clear Audit Trail Logs", type="secondary", use_container_width=True):
                    clear_audit_logs()
                    st.success("Audit logs cleared successfully!")
                    st.rerun()

            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("No audit logs recorded yet.")
