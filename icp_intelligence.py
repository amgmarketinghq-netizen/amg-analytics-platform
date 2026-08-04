"""
AMG Marketing Global — Engine 2 (Live Intelligence Engine)
Module: icp_intelligence.py
=========================================================================
Decision-Maker Hierarchy Classifier (Tier 1-4) & 0-100 ICP Score Engine
"""

import re
import numpy as np
import pandas as pd

TIER_1_KEYWORDS = ["ceo", "founder", "co-founder", "owner", "president", "chief", "cto", "cmo", "cro", "cfo", "coo", "partner"]
TIER_2_KEYWORDS = ["vice president", "vp", "director", "head of", "head", "general manager", "gm"]
TIER_3_KEYWORDS = ["manager", "lead", "supervisor", "team lead", "senior manager", "principal"]
TIER_4_KEYWORDS = ["executive", "associate", "analyst", "specialist", "coordinator", "developer", "engineer", "intern", "staff"]


def classify_decision_maker_tier(title_val):
    """Categorizes job titles into Tier 1 to Tier 4 hierarchy."""
    if pd.isna(title_val) or str(title_val).strip().lower() in ("", "nan", "none", "null"):
        return "Tier 4 — General Staff / Unmapped", 4

    t = str(title_val).lower().strip()

    for kw in TIER_1_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', t):
            return "Tier 1 — C-Suite & Founders (Primary Decision Maker)", 1

    for kw in TIER_2_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', t):
            return "Tier 2 — VPs & Directors (Budget Approvers)", 2

    for kw in TIER_3_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', t):
            return "Tier 3 — Managers & Team Leads (Evaluators)", 3

    return "Tier 4 — General Staff / End Users", 4


def calculate_icp_score(row, mapping):
    """Calculates ICP Buyer Intent Score (0 to 100) based on record authority and completeness."""
    score = 0

    title_col = mapping.get("job_title")
    email_col = mapping.get("email")
    phone_col = mapping.get("phone")
    company_col = mapping.get("company")

    # 1. Authority Weight (Max 45 Points)
    if title_col and title_col in row and pd.notna(row[title_col]):
        _, tier_num = classify_decision_maker_tier(row[title_col])
        if tier_num == 1:
            score += 45
        elif tier_num == 2:
            score += 35
        elif tier_num == 3:
            score += 20
        else:
            score += 10

    # 2. Company Identity (Max 20 Points)
    if company_col and company_col in row and pd.notna(row[company_col]):
        c_val = str(row[company_col]).strip()
        if c_val and c_val.lower() not in ("nan", "none", "null"):
            score += 20

    # 3. Direct Contactability (Max 20 Points)
    if email_col and email_col in row and pd.notna(row[email_col]):
        e_val = str(row[email_col]).strip().lower()
        if "@" in e_val:
            if not any(dom in e_val for dom in ["gmail.com", "yahoo.com", "hotmail.com"]):
                score += 20
            else:
                score += 10

    # 4. Phone Reachability (Max 15 Points)
    if phone_col and phone_col in row and pd.notna(row[phone_col]):
        p_val = str(row[phone_col]).strip()
        if len(re.sub(r'\D', '', p_val)) >= 7:
            score += 15

    return min(score, 100)


def enrich_dataframe_intelligence(df, mapping):
    """Enriches raw dataframe with Tier classification and ICP Score WITHOUT modifying raw data."""
    intel_df = df.copy()
    title_col = mapping.get("job_title")
    
    if title_col and title_col in intel_df.columns:
        intel_df["Decision_Maker_Tier"] = intel_df[title_col].apply(lambda x: classify_decision_maker_tier(x)[0])
    else:
        intel_df["Decision_Maker_Tier"] = "Tier 4 — General Staff / Unmapped"

    intel_df["ICP_Intent_Score"] = intel_df.apply(lambda row: calculate_icp_score(row, mapping), axis=1)
    return intel_df
