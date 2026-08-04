"""
AMG Enterprise Analytics & Data Command Center
Database Utility Layer: utils/database.py (v6.0 — SHA-256 Hashing & WAL Concurrency)
===================================================================================
Handles Persistent Storage for Clients, Hashed Passcodes & Audit Trails with SQLite WAL Mode.
"""

import sqlite3
import hashlib
import secrets

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
    """Initializes Database Schema with Auto-Migration for passcode_hash Column."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create Clients Table with passcode_hash
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active',
            passcode_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Auto-migration: Add passcode_hash column if missing in existing DB
    cursor.execute("PRAGMA table_info(clients)")
    columns = [column[1] for column in cursor.fetchall()]
    if "passcode_hash" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN passcode_hash TEXT")

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


def add_client(client_name: str, email: str, status: str = "Active", passcode: str = None) -> bool:
    """Adds a new client record with SHA-256 hashed passcode."""
    if not passcode:
        passcode = secrets.token_hex(4)

    pass_hash = hash_passcode(passcode)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clients (client_name, email, status, passcode_hash) VALUES (?, ?, ?, ?)",
            (client_name.strip(), email.strip().lower(), status, pass_hash)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM clients WHERE LOWER(email) = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] == "Active" if row else False


def get_all_clients():
    """Retrieves list of all registered clients including passcode_hash."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, client_name, email, status, passcode_hash, created_at FROM clients ORDER BY created_at DESC")
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
            "created_at": r[5]
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
