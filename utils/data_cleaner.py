"""
AMG Enterprise Analytics & Data Command Center
Module: utils/data_cleaner.py
===================================================================================
Core Data Cleaning, Auto-Detection, Currency Sniffing, and Quality Scoring Engine.
Calculations use pure Pandas/NumPy logic (0% AI Hallucination).
"""

import re
import pandas as pd
import numpy as np


def clean_numeric_series(raw: pd.Series):
    """
    Cleans text-formatted currency/numeric columns (e.g. "$45,000", "₹1,20,000", "(500)").
    Returns:
        numeric_series (pd.Series): Coerced float values.
        detected_currency (str or None): Currency symbol found in raw text.
    """
    if raw is None or raw.empty:
        return pd.Series(dtype=float), None

    text = raw.astype(str)
    sample = " ".join(text.dropna().head(50).tolist())
    
    # Currency symbol sniffing from raw text
    detected_currency = None
    for sym in ["₹", "$", "€", "£"]:
        if sym in sample:
            detected_currency = sym
            break

    # Clean formatting: strip currency symbols, commas, spaces
    cleaned = text.str.replace(r"[₹$€£,\s]", "", regex=True)
    # Accounting negative format: (500) -> -500
    cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return numeric, detected_currency


def detect_dataset_archetype(df: pd.DataFrame, file_name: str = "", currency_override: str = None) -> dict:
    """
    3-Layer Deep Auto-Detection Engine:
    Layer 1: Filename Keyword Inspection
    Layer 2: Header Regex Synonyms
    Layer 3: Data Cell Text Inspection (sample of 50 rows)
    """
    if df is None or df.empty:
        return {
            "archetype": "GENERAL",
            "mapping": {"email": None, "num_col": None, "num_series": None, "category_col": None, "currency_symbol": "₹"}
        }

    fname = str(file_name).lower().strip()
    cols = [str(c).lower().strip() for c in df.columns]

    # Layer 1: Filename Inspection
    fn_fine = any(k in fname for k in ["fine", "penalty", "fee", "tax", "challan", "dues", "bill", "invoice", "payment", "overdue"])
    fn_hr = any(k in fname for k in ["employee", "emp", "hr", "payroll", "salary", "staff", "workforce", "joined"])
    fn_sales = any(k in fname for k in ["sales", "deal", "pipeline", "revenue", "win", "arr", "mrr"])
    fn_lead = any(k in fname for k in ["lead", "contact", "prospect", "outreach", "b2b", "email"])

    # Layer 2: Header Synonyms
    sales_kw = ["sales", "deal", "pipeline", "stage", "arr", "mrr", "win_rate", "opportunity", "close_date"]
    b2b_kw = ["email", "lead", "company", "domain", "job_title", "title", "linkedin", "contact", "industry", "phone"]
    hr_kw = ["employee", "emp_id", "department", "dept", "designation", "salary", "doj", "joining", "payroll", "performance", "role"]
    fine_kw = ["fine", "penalty", "fee", "charge", "tax", "invoice", "overdue", "due_date", "challan", "violation", "due", "unpaid"]

    def count_matches(keywords):
        return sum(1 for kw in keywords if any(kw in c for c in cols))

    # Layer 3: Cell Content Scan
    sample_text = ""
    try:
        sample_text = " ".join(df.head(50).astype(str).values.flatten()).lower()
    except Exception:
        pass

    cell_fine = any(k in sample_text for k in ["paid", "unpaid", "pending", "gst", "challan", "penalty", "tax invoice", "overdue", "amount due"])
    cell_hr = any(k in sample_text for k in ["department", "full time", "part time", "manager", "payroll", "joining date"])
    cell_sales = any(k in sample_text for k in ["closed won", "closed lost", "qualified", "negotiation", "contract"])

    scores = {
        "FINANCIAL_FINES": (3 if fn_fine else 0) + (count_matches(fine_kw) * 2) + (2 if cell_fine else 0),
        "HR_EMPLOYEE": (3 if fn_hr else 0) + (count_matches(hr_kw) * 2) + (2 if cell_hr else 0),
        "SALES": (3 if fn_sales else 0) + (count_matches(sales_kw) * 2) + (2 if cell_sales else 0),
        "B2B_LEADS": (3 if fn_lead else 0) + (count_matches(b2b_kw) * 2),
    }
    
    max_type = max(scores, key=scores.get)
    if scores[max_type] == 0:
        max_type = "GENERAL"

    def find_column(patterns):
        for c in df.columns:
            if any(re.search(pat, str(c).lower().strip()) for pat in patterns):
                return c
        return None

    email_col = find_column([r"e[-_ ]?mail", r"contact"])
    num_col_candidate = find_column([r"revenue", r"amount", r"sales", r"value", r"price", r"salary",
                                     r"fine", r"penalty", r"fee", r"tax", r"due", r"balance", r"total", r"challan"])
    category_col = find_column([r"department", r"dept", r"stage", r"status", r"designation", r"role",
                                 r"region", r"city", r"country", r"type"])

    # Numeric Column Fallback if no candidate pattern matched
    if not num_col_candidate:
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]) and not any(k in str(c).lower() for k in ["id", "year", "zip", "code", "phone"]):
                num_col_candidate = c
                break

    detected_currency = None
    numeric_series = None
    if num_col_candidate:
        numeric_series, detected_currency = clean_numeric_series(df[num_col_candidate])
        if numeric_series.notna().sum() == 0:
            num_col_candidate = None
            numeric_series = None

    final_currency = currency_override or detected_currency or "₹"

    mapping = {
        "email": email_col,
        "num_col": num_col_candidate,
        "num_series": numeric_series,
        "category_col": category_col,
        "currency_symbol": final_currency,
    }
    return {"archetype": max_type, "mapping": mapping}


def compute_quality_metrics(df: pd.DataFrame, col_map: dict) -> dict:
    """
    Computes mathematical quality & hygiene metrics:
    - Data Quality Index (DQI: 0-100)
    - Integrity %
    - Duplicates Count
    - Email Syntax Anomalies
    - Deliverability Index %
    """
    if df is None or df.empty:
        return {
            "score": 0.0, "integrity": 0.0, "duplicates": 0, "anomalies": 0,
            "deliverability_index": 0.0, "n_rows": 0, "n_cols": 0
        }

    n_rows, n_cols = df.shape
    total_cells = max(n_rows * n_cols, 1)
    missing_ratio = df.isna().sum().sum() / total_cells
    integrity = max(0.0, 1.0 - missing_ratio)
    duplicates = int(df.duplicated().sum())
    dup_ratio = duplicates / max(n_rows, 1)
    
    mapped_fields = sum(1 for k, v in col_map.items() if k in ("email", "num_col", "category_col") and v)
    diversity = min(mapped_fields / 3.0, 1.0)
    
    anomalies = 0
    if col_map.get("email"):
        email_col = df[col_map["email"]].astype(str)
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        anomalies = int((~email_col.str.match(email_pattern)).sum())
        
    score = round(100 * (0.45 * integrity + 0.25 * diversity + 0.15 * max(0, 1 - dup_ratio) + 0.15 * max(0, 1 - anomalies / max(n_rows, 1))), 1)
    valid_syntax_ratio = max(0.0, (n_rows - anomalies) / max(n_rows, 1))
    
    return {
        "score": min(100.0, max(0.0, score)),
        "integrity": round(integrity * 100, 1),
        "duplicates": duplicates,
        "anomalies": anomalies,
        "deliverability_index": round(valid_syntax_ratio * 100, 1),
        "n_rows": n_rows,
        "n_cols": n_cols,
    }


def sanitize_dataframe(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """
    Returns a cleaned version of the DataFrame:
    - Removes duplicate rows
    - Removes invalid email syntax rows (if email column exists)
    """
    if df is None or df.empty:
        return df

    cleaned_df = df.drop_duplicates().copy()
    
    if col_map.get("email") and col_map["email"] in cleaned_df.columns:
        email_col_name = col_map["email"]
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        valid_mask = cleaned_df[email_col_name].astype(str).str.match(email_pattern)
        cleaned_df = cleaned_df[valid_mask]

    return cleaned_df
