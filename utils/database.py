"""
AMG Enterprise Analytics & Data Command Center
Utility: utils/database.py
===================================================================================
SQLite Database Handler for Client Portal Access, Auth & System Audit Logs.
Includes Clear Audit Logs capability.
"""

import sqlite3
import os

DB_PATH = "amg_enterprise.db"


def init_db():
    """Initializes SQLite database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_email TEXT NOT NULL,
            file_name TEXT NOT NULL,
            total_rows INTEGER,
            clean_rows INTEGER,
            quality_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_client(client_name: str, email: str, status: str = "Active") -> bool:
    """Adds a new client to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (client_name, email, status) VALUES (?, ?, ?)",
                       (client_name, email.strip().lower(), status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def toggle_client_status(email: str, new_status: str):
    """Toggles active/inactive status of a client."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET status = ? WHERE LOWER(email) = ?", (new_status, email.strip().lower()))
    conn.commit()
    conn.close()


def is_client_active(email: str) -> bool:
    """Checks if client is active."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM clients WHERE LOWER(email) = ?", (email.strip().lower(),))
    res = cursor.fetchone()
    conn.close()
    return res[0] == 'Active' if res else False


def get_all_clients() -> list:
    """Returns all registered clients."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY client_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def log_audit_trail(email: str, file_name: str, total_rows: int, clean_rows: int, quality_score: float):
    """Logs client file processing activity."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (client_email, file_name, total_rows, clean_rows, quality_score)
        VALUES (?, ?, ?, ?, ?)
    """, (email, file_name, total_rows, clean_rows, quality_score))
    conn.commit()
    conn.close()


def get_audit_logs() -> list:
    """Returns processing logs."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY log_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_audit_logs() -> bool:
    """Clears/deletes all records from audit logs table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audit_logs")
    conn.commit()
    conn.close()
    return True


def create_invoice():
    pass


def get_all_invoices():
    pass
