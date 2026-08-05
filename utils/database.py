"""
AMG Enterprise Analytics & Data Command Center
Database Utility Layer: utils/database.py (v6.3 — Auto Expiry Timer)
===================================================================================
Handles Persistent Storage for Clients, Hashed Passcodes, Deletion & Timed Pass Expiration.
"""

import sqlite3
import hashlib
import secrets
import datetime as dt

DB_PATH = "amg_enterprise.db"


def get_connection():
    """Returns SQLite connection with 10s timeout and WAL Mode for high concurrency."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def hash_passcode(raw: str) -> str:
    """Hashes raw passcode/PIN using SHA-256."""
    if not raw:
        return ""
    return hashlib.sha256(raw.strip().encode("utf-8")).hexdigest()


def init_db():
    """Initializes Database Schema with Auto-Migration for passcode_hash & pass_duration Columns."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create Clients Table with passcode_hash and pass_duration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active',
            passcode_hash TEXT,
            pass_duration TEXT DEFAULT 'Permanent / Lifetime',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Auto-migrations
    cursor.execute("PRAGMA table_info(clients)")
    columns = [column[1] for column in cursor.fetchall()]
    if "passcode_hash" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN passcode_hash TEXT")
    if "pass_duration" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN pass_duration TEXT DEFAULT 'Permanent / Lifetime'")

    # Create Audit Trail Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            file_name TEXT NOT NULL,
            total_rows INTEGER,
            clean_rows INTEGER,
            quality_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_client(client_name: str, email: str, status: str = "Active", passcode: str = None, pass_duration: str = "Permanent / Lifetime") -> bool:
    """Adds or resets a client record with hashed passcode, duration and fresh timestamp."""
    if not passcode:
        passcode = secrets.token_hex(4)

    pass_hash = hash_passcode(passcode)
    clean_email = email.strip().lower()
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT client_id FROM clients WHERE LOWER(email) = ?", (clean_email,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE clients SET client_name = ?, status = ?, passcode_hash = ?, pass_duration = ?, created_at = ? WHERE LOWER(email) = ?",
                (client_name.strip(), status, pass_hash, pass_duration, now_str, clean_email)
            )
        else:
            cursor.execute(
                "INSERT INTO clients (client_name, email, status, passcode_hash, pass_duration, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (client_name.strip(), clean_email, status, pass_hash, pass_duration, now_str)
            )

        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def check_client_pass_status(email: str) -> str:
    """Checks client status and automatically expires timed passes."""
    clean_email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, pass_duration, created_at FROM clients WHERE LOWER(email) = ?", (clean_email,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return "NOT_FOUND"

    status, pass_duration, created_at_str = row[0], row[1], row[2]

    if status.lower() != "active":
        conn.close()
        return "INACTIVE"

    # Check Expiration Timer
    if pass_duration and "Hours" in pass_duration:
        try:
            hours_allowed = int(pass_duration.split()[0])
            created_dt = dt.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            hours_passed = (dt.datetime.now() - created_dt).total_seconds() / 3600.0

            if hours_passed >= hours_allowed:
                # Auto-expire pass in DB
                cursor.execute("UPDATE clients SET status = 'Inactive' WHERE LOWER(email) = ?", (clean_email,))
                conn.commit()
                conn.close()
                return "EXPIRED"
        except Exception:
            pass

    conn.close()
    return "ACTIVE"


def delete_client(email: str) -> bool:
    """Permanently deletes a client record from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE LOWER(email) = ?", (email.strip().lower(),))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def toggle_client_status(email: str, new_status: str) -> bool:
    """Toggles status (Active/Inactive) for specified client."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET status = ? WHERE LOWER(email) = ?", (new_status, email.strip().lower()))
    conn.commit()
    conn.close()
    return True


def is_client_active(email: str) -> bool:
    """Checks if client account is Active."""
    return check_client_pass_status(email) == "ACTIVE"


def get_all_clients():
    """Retrieves list of all registered clients."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, client_name, email, status, passcode_hash, pass_duration, created_at FROM clients ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    clients = []
    for r in rows:
        clients.append({
            "client_id": r[0],
            "client_name": r[1],
            "email": r[2],
            "status": r[3],
            "passcode_hash": r[4],
            "pass_duration": r[5],
            "created_at": r[6]
        })
    return clients


def log_audit_trail(email: str, file_name: str, total_rows: int, clean_rows: int, quality_score: float):
    """Logs dataset upload audit details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (email, file_name, total_rows, clean_rows, quality_score) VALUES (?, ?, ?, ?, ?)",
        (email.strip().lower(), file_name, total_rows, clean_rows, quality_score)
    )
    conn.commit()
    conn.close()


def get_audit_logs():
    """Fetches all system audit logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT log_id, email, file_name, total_rows, clean_rows, quality_score, timestamp FROM audit_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "log_id": r[0],
            "email": r[1],
            "file_name": r[2],
            "total_rows": r[3],
            "clean_rows": r[4],
            "quality_score": r[5],
            "timestamp": r[6]
        })
    return logs


def clear_audit_logs():
    """Clears all logged audit trails."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audit_logs")
    conn.commit()
    conn.close()
