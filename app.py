"""
AMG Enterprise Analytics & Data Command Center
Main Application Entrypoint: app.py
===================================================================================
Integrated Multi-Dashboard SaaS Platform with Smart Client Auth,
Admin Client Search Bar, and Dual-Mode Analytics Engine.
"""

import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="AMG Enterprise Analytics Command Center",
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

# Initialize SQLite Database
init_db()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=60)
st.sidebar.title("AMG Command Center")
st.sidebar.caption("v2.5 Enterprise Edition")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Live Analytics Engine",
        "👥 Client Access Control",
        "📄 Generate HTML Invoice",
        "📜 Audit Trail Logs"
    ]
)

st.sidebar.markdown("---")

# ==========================================
# MODE 1: LIVE ANALYTICS ENGINE (SMART AUTH)
# ==========================================
if app_mode == "📊 Live Analytics Engine":
    st.sidebar.subheader("🔒 Client Authentication")
    client_email_input = st.sidebar.text_input("Enter Client Access Email:", placeholder="client@company.com")
    
    if client_email_input:
        cleaned_email = client_email_input.strip().lower()
        all_clients = get_all_clients()
        client_record = next((c for c in all_clients if c["email"].lower() == cleaned_email), None)

        if not client_record:
            st.error(f"❌ Invalid Email! `{client_email_input}` is not registered with AMG Marketing Global.")
            st.info("Please contact AMG Billing to purchase access.")
            st.stop()
        elif client_record["status"].lower() != "active":
            st.warning(f"⚠️ Account Inactive for `{client_email_input}`. Please renew your portal subscription.")
            st.stop()
        else:
            st.sidebar.success(f"✅ Welcome {client_record['client_name']}!")

    st.sidebar.subheader("📁 Upload Data Batch")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Auto-Detection Layer
            detection_res = detect_dataset_archetype(df, file_name=uploaded_file.name)
            archetype = detection_res["archetype"]
            col_map = detection_res["mapping"]

            st.sidebar.markdown("---")
            st.sidebar.subheader("🎯 Auto-Detected Type")
            st.sidebar.info(f"**Archetype:** `{archetype}`")

            # Override Archetype
            selected_dashboard = st.sidebar.selectbox(
                "Switch Dashboard View:",
                ["Auto-Select", "Sales & Revenue", "Customer / Leads", "HR & Payroll", "E-Commerce", "Marketing ROI"]
            )

            if selected_dashboard != "Auto-Select":
                override_dict = {
                    "Sales & Revenue": "SALES",
                    "Customer / Leads": "B2B_LEADS",
                    "HR & Payroll": "HR_EMPLOYEE",
                    "E-Commerce": "FINANCIAL_FINES",
                    "Marketing ROI": "GENERAL"
                }
                archetype = override_dict[selected_dashboard]

            # Audit Logging
            if client_email_input:
                metrics = compute_quality_metrics(df, col_map)
                clean_df = sanitize_dataframe(df, col_map)
                log_audit_trail(
                    email=client_email_input,
                    file_name=uploaded_file.name,
                    total_rows=len(df),
                    clean_rows=len(clean_df),
                    quality_score=metrics["score"]
                )

            # Render Matching Dashboard Module
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
            st.error(f"Error processing file: {e}")
    else:
        st.title("⚡ AMG Enterprise Data Infrastructure Platform")
        st.write("Upload a CSV/Excel file in the sidebar to begin analytics & raw data sanitation.")


# ==========================================
# MODE 2: CLIENT ACCESS CONTROL (WITH SEARCH)
# ==========================================
elif app_mode == "👥 Client Access Control":
    st.title("👥 Client Portal Access & Access Toggle")
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
        st.subheader("⚙️ Manage Active / Inactive Access")
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


# ==========================================
# MODE 3: GENERATE HTML INVOICE
# ==========================================
elif app_mode == "📄 Generate HTML Invoice":
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


# ==========================================
# MODE 4: AUDIT TRAIL LOGS
# ==========================================
elif app_mode == "📜 Audit Trail Logs":
    st.title("📜 Data Audit & Processing Logs")
    st.markdown("---")

    logs = get_audit_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.info("No audit logs recorded yet. Upload data in Live Engine mode to create logs.")
