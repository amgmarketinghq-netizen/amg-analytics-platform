"""
AMG Marketing Global — Client Access & Expiry Guard
Module: pass_guard.py
=========================================================================
Admin Managed Client Email Activation with Secrets-Based Authorization
"""

import datetime as dt
import streamlit as st

# Session state DB initialization
if "client_access_db" not in st.session_state:
    st.session_state["client_access_db"] = {}
    
    # Load Master VIP Email safely from Streamlit Secrets if available
    try:
        vip_email = st.secrets.get("ADMIN_EMAIL", "").strip().lower()
        if vip_email:
            st.session_state["client_access_db"][vip_email] = {
                "duration": "PERMANENT",
                "hours": None,
                "activated_at": dt.datetime.now(dt.timezone.utc),
                "is_active": True,
                "label": "Master Admin VIP Pass"
            }
    except Exception:
        pass


def add_or_update_client(email, duration_type, label="Client"):
    """Adds or updates a client email with selected duration in the access DB."""
    clean_email = (email or "").strip().lower()
    if not clean_email or "@" not in clean_email:
        return False, "Invalid Email Address!"

    hours_map = {"24 Hours": 24, "48 Hours": 48, "72 Hours": 72, "Permanent": None}
    
    st.session_state["client_access_db"][clean_email] = {
        "duration": duration_type.upper(),
        "hours": hours_map.get(duration_type, None),
        "activated_at": dt.datetime.now(dt.timezone.utc),
        "is_active": True,
        "label": label
    }
    return True, f"Client {clean_email} activated with {duration_type} access!"


def toggle_client_status(email):
    """Manually activates or deactivates a client access."""
    clean_email = (email or "").strip().lower()
    if clean_email in st.session_state["client_access_db"]:
        current = st.session_state["client_access_db"][clean_email]["is_active"]
        st.session_state["client_access_db"][clean_email]["is_active"] = not current
        return True
    return False


def verify_client_email_access(email_input):
    """Verifies client login status based on Email, Manual Toggle, and Time Expiry."""
    clean_email = (email_input or "").strip().lower()

    if not clean_email:
        return False, "Please enter your registered Email ID.", None

    db = st.session_state.get("client_access_db", {})

    if clean_email not in db:
        return False, "Email not registered. Please contact AMG Administration.", None

    client_record = db[clean_email]

    # 1. Manual Admin Deactivation Check
    if not client_record.get("is_active", True):
        return False, "🚫 Access Suspended by AMG Administration.", client_record

    # 2. Permanent Access Check
    if client_record.get("duration") == "PERMANENT" or client_record.get("hours") is None:
        return True, "✅ Permanent VIP Access Granted.", client_record

    # 3. Time Expiry Check (24h / 48h / 72h)
    activated_time = client_record["activated_at"]
    now_utc = dt.datetime.now(dt.timezone.utc)
    elapsed_hours = (now_utc - activated_time).total_seconds() / 3600.0
    allowed_hours = client_record["hours"]

    if elapsed_hours > allowed_hours:
        client_record["is_active"] = False
        return False, f"🔒 Access Expired! ({allowed_hours} Hours Pass Limit Reached)", client_record

    remaining = max(0.0, allowed_hours - elapsed_hours)
    return True, f"✅ Access Active ({remaining:.1f} Hours Remaining)", client_record


def render_admin_client_manager():
    """Renders the Admin Control Panel to Add/Manage Clients."""
    st.subheader("👥 Registered Clients Access Registry")
    
    with st.expander("➕ Register & Activate New Client Pass", expanded=True):
        col1, col2, col3 = st.columns([2, 1.5, 1])
        with col1:
            new_email = st.text_input("Client Email Address", placeholder="client@company.com")
        with col2:
            duration = st.selectbox("Access Pass Duration", ["24 Hours", "48 Hours", "72 Hours", "Permanent"])
        with col3:
            st.write("")
            st.write("")
            if st.button("Activate Pass", use_container_width=True):
                success, msg = add_or_update_client(new_email, duration)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    db = st.session_state.get("client_access_db", {})

    if not db:
        st.info("No active clients registered yet.")
        return

    for email, record in list(db.items()):
        status_color = "🟢 Active" if record.get("is_active", True) else "🔴 Inactive/Blocked"
        dur_label = f"{record['hours']}h Pass" if record.get('hours') else "Permanent VIP"
        
        c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.5, 1])
        with c1:
            st.markdown(f"**{email}**")
            st.caption(f"Status: {status_color} | Type: {dur_label}")
        with c2:
            st.caption(f"Activated: {record['activated_at'].strftime('%d %b, %H:%M UTC')}")
        with c3:
            btn_text = "Deactivate" if record.get("is_active", True) else "Re-Activate"
            if st.button(btn_text, key=f"tog_{email}", use_container_width=True):
                toggle_client_status(email)
                st.rerun()
        with c4:
            if st.button("🗑️", key=f"del_{email}"):
                del st.session_state["client_access_db"][email]
                st.rerun()


def verify_access_key(key_input):
    return verify_client_email_access(key_input)

def render_lock_screen():
    pass
