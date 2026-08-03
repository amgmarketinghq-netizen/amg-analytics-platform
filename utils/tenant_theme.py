"""
AMG Enterprise Analytics & Data Command Center
Utility: utils/tenant_theme.py
===================================================================================
Pillar 1: White-Label Enterprise Branding Engine.
Injects dynamic tenant CSS, custom logo headers, and Plotly executive color schemes.
"""

import streamlit as st


def apply_tenant_theme(agency_name="AMG Marketing Global", primary_hex="#0284c7"):
    """Injects high-end corporate styling and white-label theme into Streamlit."""
    custom_css = f"""
    <style>
        /* Top Header Styling */
        .stAppViewContainer {{
            background-color: #f8fafc;
        }}
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}
        /* Metric Card Customization */
        [data-testid="stMetricValue"] {{
            font-weight: 700;
            color: {primary_hex};
        }}
        /* Tabs Styling */
        button[data-baseweb="tab"] {{
            font-weight: 600;
            font-size: 15px;
        }}
        /* Executive Header Banner */
        .executive-header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 20px 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .executive-header h2 {{
            margin: 0;
            color: #38bdf8;
            font-size: 22px;
        }}
        .executive-header p {{
            margin: 4px 0 0 0;
            color: #94a3b8;
            font-size: 13px;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
