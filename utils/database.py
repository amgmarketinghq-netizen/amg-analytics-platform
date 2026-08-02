"""
AMG Enterprise Analytics & Data Command Center
Module: utils/database.py
===================================================================================
Database Management Engine (SQLite / Supabase Ready).
Handles Client Access Control (ON/OFF), Audit Logs, and Invoice Records.
Calculations use exact numerical aggregations (0% AI Hallucination).
"""

import sqlite3
import datetime
import os
from typing import List, Dict, Any, Optional

DB_PATH = "amg_analytics.db"


def get_connection():
    """Establishes connection to the local SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes necessary database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Clients Table (Access Toggle Control)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active', -- 'Active' or 'Inactive'
                created_at TEXT NOT NULL
            )
        """)
        
        # 2. Audit Trail Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_email TEXT NOT NULL,
                file_name TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                clean_rows INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # 3. Manual Invoices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT '₹',
                payment_status TEXT NOT NULL DEFAULT 'Unpaid', -- 'Paid' or 'Unpaid'
                created_date TEXT NOT NULL,
                due_date TEXT NOT NULL
            )
        """)
        
        conn.commit()


# ==========================================
# CLIENT ACCESS MANAGEMENT (ON / OFF TOGGLE)
# ==========================================

def add_client(client_name: str, email: str, status: str = "Active") -> bool:
    """Adds a new client to the database."""
    init_db()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO clients (client_name, email, status, created_at) VALUES (?, ?, ?, ?)",
                (client_name, email.strip().lower(), status, created_at)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # Email already exists


def toggle_client_status(email: str, new_status: str) -> bool:
    """Toggles client status between 'Active' and 'Inactive'."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE clients SET status = ? WHERE LOWER(email) = ?",
            (new_status, email.strip().lower())
        )
        conn.commit()
        return cursor.rowcount > 0


def is_client_active(email: str) -> bool:
    """Checks whether a client has active access."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM clients WHERE LOWER(email) = ?",
            (email.strip().lower(),)
        )
        row = cursor.fetchone()
        if row:
            return row["status"].lower() == "active"
        return False  # Default to False if client not found


def get_all_clients() -> List[Dict[str, Any]]:
    """Retrieves all registered clients."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY client_id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ==========================================
# AUDIT LOGGING ENGINE
# ==========================================

def log_audit_trail(email: str, file_name: str, total_rows: int, clean_rows: int, quality_score: float):
    """Logs data cleaning jobs for complete audit history."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO audit_logs (client_email, file_name, total_rows, clean_rows, quality_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email.strip().lower(), file_name, int(total_rows), int(clean_rows), float(quality_score), timestamp))
        conn.commit()


def get_audit_logs(email: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves audit logs, optionally filtered by client email."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        if email:
            cursor.execute("SELECT * FROM audit_logs WHERE LOWER(client_email) = ? ORDER BY log_id DESC", (email.strip().lower(),))
        else:
            cursor.execute("SELECT * FROM audit_logs ORDER BY log_id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ==========================================
# INVOICE MANAGEMENT ENGINE
# ==========================================

def create_invoice(invoice_id: str, client_name: str, client_email: str, amount: float, currency: str = "₹", payment_status: str = "Unpaid") -> bool:
    """Creates a new manual invoice record."""
    init_db()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            created_date = datetime.date.today().strftime("%Y-%m-%d")
            due_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO invoices (invoice_id, client_name, client_email, amount, currency, payment_status, created_date, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (invoice_id, client_name, client_email.strip().lower(), float(amount), currency, payment_status, created_date, due_date))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def update_invoice_status(invoice_id: str, new_status: str) -> bool:
    """Updates invoice payment status ('Paid' or 'Unpaid')."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE invoices SET payment_status = ? WHERE invoice_id = ?",
            (new_status, invoice_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def get_all_invoices() -> List[Dict[str, Any]]:
    """Retrieves all invoices for billing management."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices ORDER BY created_date DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
