"""
AMG Enterprise Analytics & Data Command Center
Database Utility Layer: utils/database.py (v6.5 — Security & Global Lockout Edition)
===================================================================================
Handles Persistent Storage, SHA-256 Hashing, DB-backed Lockouts & Timed Expiration.
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
    """Initializes Database Schema with Auto-Migration & Lockout Tracking."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create Clients Table
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

    # Create Lockouts Table (Prevents Incognito Bypass)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_lockouts (
            identifier TEXT PRIMARY KEY,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
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


def record_failed_attempt(identifier: str) -> bool:
    """Tracks failed login attempts in DB to prevent incognito lockout bypass."""
    clean_id = identifier.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT failed_attempts FROM login_lockouts WHERE identifier = ?", (clean_id,))
    row = cursor.fetchone()

    if row:
        attempts = row[0] + 1
        locked_until = None
        if attempts >= 5:
            locked_until = (dt.datetime.now() + dt.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE login_lockouts SET failed_attempts = ?, locked_until = ? WHERE identifier = ?",
            (attempts, locked_until, clean_id)
        )
    else:
        cursor.execute(
            "INSERT INTO login_lockouts (identifier, failed_attempts) VALUES (?, 1)",
            (clean_id,)
        )

    conn.commit()
    conn.close()
    return True


def check_lockout(identifier: str) -> int:
    """Returns remaining seconds if locked out, or 0 if accessible."""
    clean_id = identifier.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT locked_until FROM login_lockouts WHERE identifier = ?", (clean_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        locked_dt = dt.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if dt.datetime.now() < locked_dt:
            return int((locked_dt - dt.datetime.now()).total_seconds())
        else:
            reset_lockout(clean_id)
    return 0


def reset_lockout(identifier: str):
    """Resets failed attempt counters upon successful login."""
    clean_id = identifier.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM login_lockouts WHERE identifier = ?", (clean_id,))
    conn.commit()
    conn.close()


def add_client(client_name: str, email: str, status: str = "Active", passcode: str = None, pass_duration: str = "Permanent / Lifetime") -> bool:
    """Adds or resets a client record with hashed passcode and duration."""
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

    if status and status.lower() != "active":
        conn.close()
        return "INACTIVE"

    if pass_duration and "Hours" in str(pass_duration):
        try:
            hours_allowed = int(str(pass_duration).split()[0])
            created_dt = dt.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            hours_passed = (dt.datetime.now() - created_dt).total_seconds() / 3600.0

            if hours_passed >= hours_allowed:
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
            "pass_duration": r[5] if len(r) > 5 else "Permanent / Lifetime",
            "created_at": r[6] if len(r) > 6 else ""
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
