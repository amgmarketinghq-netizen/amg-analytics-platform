"""
AMG Marketing Global — Engine 2 (Live Intelligence Engine)
Module: pass_guard.py
=========================================================================
Time-Bound Access Key Controller (24h / 48h / 72h / Permanent VIP)
"""

import datetime as dt
import streamlit as st

VALID_PASSES = {
    # Permanent Access Keys (Never Expire)
    "AMG-VIP-PERMANENT-ACCESS": {"type": "PERMANENT", "hours": None, "label": "AMG Admin / Secondary Account"},
    "AMG-PASS-VIP-HAIDAR": {"type": "PERMANENT", "hours": None, "label": "Haidar Personal VIP Pass"},

    # Demo 24h / 48h / 72h Test Keys
    "AMG-PASS-ONEINFER-24H": {"type": "24H", "hours": 24, "label": "OneInfer 24-Hour Trial Pass"},
    "AMG-PASS-CLIENT-48H": {"type": "48H", "hours": 48, "label": "Standard Agency 48-Hour Pass"},
    "AMG-PASS-AUDIT-72H": {"type": "72H", "hours": 72, "label": "Enterprise Weekend Audit Pass"},
}


def verify_access_key(key_input):
    """Verifies if the provided key is valid and not expired."""
    clean_key = (key_input or "").strip()
    
    if not clean_key:
        return False, "Key missing", None

    if clean_key not in VALID_PASSES:
        return False, "Invalid Access Key", None

    pass_info = VALID_PASSES[clean_key]
    pass_type = pass_info["type"]

    # Permanent Keys never expire
    if pass_type == "PERMANENT":
        return True, "VIP Permanent Access Granted (No Expiration)", pass_info

    # Time-bound Keys (24h / 48h / 72h)
    if f"key_activated_{clean_key}" not in st.session_state:
        st.session_state[f"key_activated_{clean_key}"] = dt.datetime.now(dt.timezone.utc)

    activation_time = st.session_state[f"key_activated_{clean_key}"]
    now_utc = dt.datetime.now(dt.timezone.utc)
    elapsed_hours = (now_utc - activation_time).total_seconds() / 3600.0

    allowed_hours = pass_info["hours"]

    if elapsed_hours > allowed_hours:
        return False, f"🔒 Access Pass Expired! ({allowed_hours}h limit exceeded)", pass_info

    remaining_hours = max(0.0, allowed_hours - elapsed_hours)
    return True, f"Active Pass ({remaining_hours:.1f} Hours Remaining)", pass_info


def render_lock_screen():
    """Renders the security lock screen if key is invalid or expired."""
    st.markdown("""
    <div style="background-color: #1A1F2B; border: 2px solid #E06666; padding: 30px; border-radius: 12px; text-align: center; margin-top: 50px;">
        <h1 style="color: #E06666; margin-bottom: 10px;">🔒 SECURITY LOCK — ACCESS REQUIRED</h1>
        <p style="color: #CBD5E1; font-size: 16px;">
            This is <b>AMG Engine 2 (Live Executive Intelligence & ICP Analytics Dashboard)</b>.<br>
            Access requires an active time-bound pass key (24h / 48h / 72h) or Permanent VIP authorization.
        </p>
    </div>
    """, unsafe_allow_html=True)
