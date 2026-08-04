"""
AMG Marketing Global — Client Email Access & Expiry Controller
Module: pass_guard.py
=========================================================================
Admin Managed Client Email Activation with 24h / 48h / 72h / Permanent Limits
"""

import datetime as dt
import streamlit as st

# Default Master Client Access Store in Session State
if "client_access_db" not in st.session_state:
    st.session_state["client_access_db"] = {
        # Default Backup / Permanent Accounts
        "mdhaidara451@gmail.com": {
            "duration": "PERMANENT",
            "hours": None,
            "activated_at": dt.datetime.now(dt.timezone.utc),
            "is_active": True,
            "label": "Haidar Personal Secondary Email"
        }
    }


def add_or_update_client(email, duration_type, label="Client"):
    """Adds or updates a client email with selected duration in the access DB."""
    clean_email = email.strip().lower()
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
    clean_email = email.strip().lower()
    if clean_email in st.session_state["client_access_db"]:
        current_state = st.session_state["client_access_db"][clean_email]["is_active"]
        st.session_state["client_access_db"][clean_email]["is_active"] = not current_state
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
    if not client_record["is_active"]:
        return False, "🚫 Access Suspended by AMG Administration.", client_record

    # 2. Permanent Access Check
    if client_record["duration"] == "PERMANENT" or client_record["hours"] is None:
        return True, "✅ Permanent VIP Access Granted.", client_record

    # 3. Time Expiry Check (24h / 48h / 72h)
    activated_time = client_record["activated_at"]
    now_utc = dt.datetime.now(dt.timezone.utc)
    elapsed_hours = (now_utc - activated_time).total_seconds() / 3600.0
    allowed_hours = client_record["hours"]

    if elapsed_hours > allowed_hours:
        # Auto Deactivate on Expiry
        client_record["is_active"] = False
        return False, f"🔒 Access Expired! ({allowed_hours} Hours Pass Limit Reached)", client_record

    remaining = max(0.0, allowed_hours - elapsed_hours)
    return True, f"✅ Access Active ({remaining:.1f} Hours Remaining)", client_record


def render_admin_client_manager():
    """Renders the Admin Dashboard Control Panel to Add/Manage Clients."""
    st.subheader("👑 AMG Admin — Client Access Manager")
    
    with st.expander("➕ Register & Activate New Client Email", expanded=True):
        col1, col2, col3 = st.columns([2, 1.5, 1])
        with col1:
            new_email = st.text_input("Client Email Address", placeholder="client@company.com")
        with col2:
            duration = st.selectbox("Access Duration", ["24 Hours", "48 Hours", "72 Hours", "Permanent"])
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
    st.write("📋 **Registered Clients Access Registry:**")
    db = st.session_state.get("client_access_db", {})

    if not db:
        st.info("No active clients registered yet.")
        return

    for email, record in list(db.items()):
        status_color = "🟢 Active" if record["is_active"] else "🔴 Inactive/Blocked"
        dur_label = f"{record['hours']}h" if record['hours'] else "Permanent"
        
        c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.5, 1])
        with c1:
            st.markdown(f"**{email}**")
            st.caption(f"Status: {status_color} | Pass: {dur_label}")
        with c2:
            st.caption(f"Activated: {record['activated_at'].strftime('%d %b, %H:%M UTC')}")
        with c3:
            btn_text = "Deactivate" if record["is_active"] else "Re-Activate"
            if st.button(btn_text, key=f"tog_{email}", use_container_width=True):
                toggle_client_status(email)
                st.rerun()
        with c4:
            if st.button("🗑️", key=f"del_{email}"):
                del st.session_state["client_access_db"][email]
                st.rerun()
