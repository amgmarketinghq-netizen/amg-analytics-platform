"""
AMG Enterprise Analytics & Data Command Center
Main Application Entrypoint: app.py
===================================================================================
Integrated Multi-Dashboard SaaS Platform with Role-Based Access Security (RBAC).
Clients get 0% Admin menu access. Admin gets secret passcode control.
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

# Import Utilities
from utils.data_cleaner import detect_dataset_archetype, compute_quality_metrics, sanitize_dataframe
from utils.database import (
    init_db, add_client, toggle_client_status, is_client_active, 
    get_all_clients, log_audit_trail, get_audit_logs, create_invoice, get_all_invoices
)
from utils.invoice_generator import generate_invoice_html

# Import Dashboard Modules
from modules.sales_dashboard import render_sales_dashboard
from modules.customer_behavior import render_customer_behavior
from modules.hr_analytics import render_hr_analytics
from modules.ecommerce_hub import render_ecommerce_hub
from modules.marketing_roi import render_marketing_roi

# Initialize Database
init_db()

# Secret Admin Passcode
ADMIN_PASSCODE = "amg2026"

# Sidebar Header
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=60)
st.sidebar.title("AMG Command Center")
st.sidebar.caption("v2.5 Enterprise Edition")
st.sidebar.markdown("---")

# Role Switcher
portal_mode = st.sidebar.radio("Select Access Mode:", ["👤 Client Portal", "🔑 Admin Panel"])
st.sidebar.markdown("---")

# ==========================================
# MODE 1: CLIENT PORTAL (100% SECURE - NO ADMIN MENUS)
# ==========================================
if portal_mode == "👤 Client Portal":
    st.sidebar.subheader("🔒 Client Authentication")
    client_email_input = st.sidebar.text_input("Enter Registered Email:", placeholder="client@company.com")

    if not client_email_input:
        st.title("⚡ AMG Enterprise Data Infrastructure Platform")
        st.info("👈 Please enter your registered client email in the sidebar to access your portal.")
        st.stop()

    cleaned_email = client_email_input.strip().lower()
    all_clients = get_all_clients()
    client_record = next((c for c in all_clients if c["email"].lower() == cleaned_email), None)

    if not client_record:
        st.error(f"❌ Access Denied! Email `{client_email_input}` is not registered with AMG Marketing Global.")
        st.info("Please contact AMG Billing to purchase access.")
        st.stop()
    elif client_record["status"].lower() != "active":
        st.warning(f"⚠️ Account Suspended! Portal access for `{client_email_input}` is currently INACTIVE.")
        st.info("Please contact AMG Support to activate your access.")
        st.stop()
    else:
        st.sidebar.success(f"✅ Welcome {client_record['client_name']}")

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
            
            # Log audit trail safely
            log_audit_trail(
                email=cleaned_email,
                file_name=uploaded_file.name,
                total_rows=len(df),
                clean_rows=len(clean_df),
                quality_score=metrics["score"]
            )

            # Render Dashboard Module
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

        except Exception as e:
            st.error(f"Error processing dataset: {e}")
    else:
        st.title(f"👋 Welcome, {client_record['client_name']}!")
        st.write("Upload a CSV or Excel dataset in the sidebar to generate live executive analytics and audit health reports.")


# ==========================================
# MODE 2: ADMIN PANEL (PROTECTED WITH PASSCODE)
# ==========================================
else:
    st.sidebar.subheader("🔑 Admin Security")
    admin_input = st.sidebar.text_input("Enter Admin Passcode:", type="password")

    if admin_input != ADMIN_PASSCODE:
        st.title("🔒 AMG Admin Command Center")
        st.warning("⚠️ Restricted Area. Please enter the valid Admin Passcode in the sidebar to unlock control tools.")
        st.stop()

    st.sidebar.success("✅ Admin Authenticated")

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

    # ADMIN FEATURE 3: INVOICE GENERATOR
    elif admin_menu == "📄 Generate HTML Invoice":
        st.title("📄 Professional Invoice Generator Engine")
        st.markdown("---")

        col_a, col_b = st.columns(2)

        with col_a:
            inv_id = st.text_input("Invoice ID", value="INV-2026-001")
            client_n = st.text_input("Client Name", placeholder="HLM Contact Center")
            client_e = st.text_input("Client Email", placeholder="suvaisha@hlm.com")
            curr = st.selectbox("Currency", ["₹", "$", "€", "£"])
            
            st.markdown("---")
            service_desc = st.text_input("Service Description", value="Data Sanitation, Deduplication & Analytics Suite")
            service_amt = st.number_input("Service Amount", value=500.0, step=50.0)
            tax_pct = st.number_input("Tax Rate (%)", value=0.0)
            disc_pct = st.number_input("Discount (%)", value=0.0)

        with col_b:
            st.subheader("👁️ Live Invoice Preview")
            items = [{"description": service_desc, "amount": service_amt}]
            html_out = generate_invoice_html(inv_id, client_n, client_e, items, curr, tax_pct, disc_pct)
            st.components.v1.html(html_out, height=500, scrolling=True)

            st.download_button(
                label="📥 Download HTML Invoice",
                data=html_out,
                file_name=f"Invoice_{inv_id}.html",
                mime="text/html"
            )

    # ADMIN FEATURE 4: AUDIT LOGS
    elif admin_menu == "📜 View Audit Trail Logs":
        st.title("📜 System Audit & Client Usage Logs")
        st.markdown("---")

        logs = get_audit_logs()
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("No audit logs recorded yet.")
