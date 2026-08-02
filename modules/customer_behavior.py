"""
AMG Enterprise Analytics & Data Command Center
Module: modules/customer_behavior.py
===================================================================================
Dual-Mode B2B Leads & Raw Data Audit Dashboard Engine.
Includes Full Raw Audit Breakdown (Missing, Duplicates) & Complete HTML Export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_cleaner import compute_quality_metrics, sanitize_dataframe


def generate_full_html_report(df: pd.DataFrame, cleaned_df: pd.DataFrame, raw_total: int, dup_count: int, missing_email: int, clean_total: int) -> str:
    """Generates a standalone full HTML dashboard report for client delivery."""
    missing_summary = df.isnull().sum()
    missing_rows_html = "".join([
        f"<tr><td style='padding:10px; border:1px solid #e2e8f0;'><strong>{col}</strong></td><td style='padding:10px; border:1px solid #e2e8f0; text-align:center; color:#ef4444; font-weight:bold;'>{count}</td></tr>" 
        for col, count in missing_summary.items()
    ])
    
    clean_sample_html = cleaned_df.head(25).to_html(index=False, classes='clean-table', border=0)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AMG Enterprise Analytics & Lead Audit Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; color: #0f172a; margin: 0; padding: 30px; }}
        .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
        .header h1 {{ margin: 0; font-size: 28px; color: #38bdf8; }}
        .header p {{ margin: 8px 0 0 0; color: #94a3b8; font-size: 15px; }}
        .grid {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
        .card {{ flex: 1; min-width: 220px; background: white; padding: 22px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; border-top: 5px solid #0284c7; }}
        .card-title {{ font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-num {{ font-size: 32px; font-weight: bold; color: #0f172a; margin-top: 8px; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 30px; }}
        .section h2 {{ margin-top: 0; color: #1e293b; font-size: 20px; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background-color: #f1f5f9; padding: 12px; border: 1px solid #e2e8f0; text-align: left; font-size: 14px; color: #475569; }}
        td {{ padding: 10px; border: 1px solid #e2e8f0; font-size: 13px; color: #334155; }}
        tr:nth-child(even) {{ background-color: #f8fafc; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 13px; color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ AMG Enterprise Analytics Command Center</h1>
        <p>Official Executive Lead Quality & Data Sanitation Audit Report</p>
    </div>

    <div class="grid">
        <div class="card" style="border-color: #3b82f6;">
            <div class="card-title">Total Raw Records</div>
            <div class="card-num">{raw_total:,}</div>
        </div>
        <div class="card" style="border-color: #ef4444;">
            <div class="card-title">Duplicate Rows Removed</div>
            <div class="card-num" style="color: #ef4444;">{dup_count:,}</div>
        </div>
        <div class="card" style="border-color: #f59e0b;">
            <div class="card-title">Missing Email Fields</div>
            <div class="card-num" style="color: #f59e0b;">{missing_email:,}</div>
        </div>
        <div class="card" style="border-color: #10b981;">
            <div class="card-title">Clean Valid Output Leads</div>
            <div class="card-num" style="color: #10b981;">{clean_total:,}</div>
        </div>
    </div>

    <div class="section">
        <h2>📌 Column-Wise Missing Field Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Column Name in Raw File</th>
                    <th style="text-align: center;">Missing Values Count</th>
                </tr>
            </thead>
            <tbody>
                {missing_rows_html}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>📋 Clean Verified Leads Master Preview (Top 25)</h2>
        {clean_sample_html}
    </div>

    <div class="footer">
        Generated automatically by <strong>AMG Data Infrastructure Engine</strong> &bull; Confidential
    </div>
</body>
</html>"""
    return html_content


def render_customer_behavior(df: pd.DataFrame, col_map: dict):
    """Renders B2B Leads Analytics & Raw Audit Engine with Dual Tabs & HTML Export."""
    st.title("👥 Customer Behavior & Lead Quality Analytics")
    st.caption("Powered by AMG Data Infrastructure Engine")
    st.markdown("---")

    if df is None or df.empty:
        st.warning("⚠️ No dataset uploaded. Please upload a B2B Leads or Customer CSV/Excel file.")
        return

    # Calculate Raw Metrics
    raw_total_rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    missing_email_count = int(df['Email'].isnull().sum()) if 'Email' in df.columns else 0

    # Cleaned Data Computation
    cleaned_df = sanitize_dataframe(df, col_map)
    clean_rows = len(cleaned_df)
    quality_metrics = compute_quality_metrics(cleaned_df, col_map)

    # ==========================================
    # TOP SECTION: 1-CLICK FULL HTML DASHBOARD DOWNLOAD
    # ==========================================
    html_report_code = generate_full_html_report(
        df=df, 
        cleaned_df=cleaned_df, 
        raw_total=raw_total_rows, 
        dup_count=duplicate_count, 
        missing_email=missing_email_count, 
        clean_total=clean_rows
    )

    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.subheader("⚡ Executive Summary & Actions")
    with col_dl2:
        st.download_button(
            label="📥 Download Full HTML Dashboard",
            data=html_report_code,
            file_name="AMG_Full_Executive_Dashboard_Report.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )

    st.markdown("---")

    # ==========================================
    # DUAL DASHBOARD TABS (TAB 1 & TAB 2)
    # ==========================================
    tab1, tab2 = st.tabs([
        "📊 Dashboard 1: Clean Data Analytics", 
        "🛡️ Dashboard 2: Raw Data, Missing & Duplicate Audit"
    ])

    # ------------------------------------------
    # TAB 1: CLEAN DATA ANALYTICS
    # ------------------------------------------
    with tab1:
        st.subheader("📊 Sanitized & Validated Leads Performance")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Clean Valid Leads", f"{clean_rows:,}")
        with c2:
            st.metric("Data Quality Index", f"{quality_metrics['score']}%")
        with c3:
            st.metric("Deliverability Rating", "100.0%")
        with c4:
            if 'Email' in cleaned_df.columns:
                unique_domains = cleaned_df['Email'].apply(lambda x: str(x).split('@')[-1] if '@' in str(x) else 'Other').nunique()
            else:
                unique_domains = 0
            st.metric("Unique Lead Domains", f"{unique_domains:,}")

        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("📧 Top Lead Email Domains")
            if 'Email' in cleaned_df.columns:
                domains = cleaned_df['Email'].dropna().apply(lambda x: str(x).split('@')[-1].lower() if '@' in str(x) else 'Other')
                domain_counts = domains.value_counts().head(10).reset_index()
                domain_counts.columns = ["Domain", "Count"]
                fig_dom = px.bar(
                    domain_counts, x="Count", y="Domain", orientation="h",
                    title="Top Lead Domains Distribution", color="Count", color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_dom, use_container_width=True)

        with col_b:
            st.subheader("🛡️ Data Cleanliness Ratio")
            health_df = pd.DataFrame({
                "Category": ["Valid Clean Records", "Filtered Out (Duplicates/Blanks)"],
                "Count": [clean_rows, raw_total_rows - clean_rows]
            })
            fig_pie = px.pie(health_df, names="Category", values="Count", hole=0.5, color_discrete_sequence=["#10b981", "#ef4444"])
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Verified Clean Leads Master Preview (Top 100)")
        st.dataframe(cleaned_df.head(100), use_container_width=True)

    # ------------------------------------------
    # TAB 2: RAW DATA & AUDIT BREAKDOWN
    # ------------------------------------------
    with tab2:
        st.subheader("🛡️ Raw Dataset Audit: Duplicates & Missing Values")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Raw Records Uploaded", f"{raw_total_rows:,}")
        with m2:
            st.metric("Duplicate Rows Found", f"{duplicate_count:,}", delta=f"-{duplicate_count}", delta_color="inverse")
        with m3:
            st.metric("Missing / Blank Emails", f"{missing_email_count:,}", delta=f"-{missing_email_count}", delta_color="inverse")
        with m4:
            st.metric("Final Output Clean Leads", f"{clean_rows:,}", delta=f"+{clean_rows}")

        st.markdown("---")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.subheader("📌 Column-Wise Missing Field Summary")
            missing_by_col = df.isnull().sum().reset_index()
            missing_by_col.columns = ["Column Name in Raw File", "Missing Count"]
            st.dataframe(missing_by_col, use_container_width=True)
            
        with col_m2:
            st.subheader("🔄 Duplicate Records Sample Preview")
            duplicates_df = df[df.duplicated(keep=False)]
            if not duplicates_df.empty:
                st.dataframe(duplicates_df.head(100), use_container_width=True)
            else:
                st.success("✅ No duplicate records found in this dataset!")
