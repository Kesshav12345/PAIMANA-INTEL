"""
PAIMANA Deterministic Formula Registry
Version: 1.0.0
Author: Antigravity Architect

This module defines deterministic, pure functions for computing PAIMANA project metrics.
Null Behavior: Functions strictly handle missing values by returning None, rather than 0.
Denominator-Zero Behavior: Returns None or handles appropriately without raising exceptions.
"""

from typing import Optional
import datetime
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

def _is_missing(val):
    return val is None or pd.isna(val) or val == ""

def compute_financial_progress(cumulative_expenditure: Optional[float], anticipated_cost: Optional[float]) -> Optional[float]:
    """
    Definition: (Cumulative Expenditure / Anticipated Cost) * 100
    Null Behavior: Returns None if either input is None, or if anticipated_cost is 0.
    """
    if _is_missing(cumulative_expenditure) or _is_missing(anticipated_cost) or anticipated_cost == 0:
        return None
    return round((cumulative_expenditure / anticipated_cost) * 100, 2)

def compute_cost_overrun_amount(anticipated_cost: Optional[float], original_cost: Optional[float]) -> Optional[float]:
    """
    Definition: Anticipated Cost - Original Cost
    Null Behavior: Returns None if either is None.
    """
    if _is_missing(anticipated_cost) or _is_missing(original_cost):
        return None
    return round(anticipated_cost - original_cost, 2)

def compute_cost_overrun_pct(anticipated_cost: Optional[float], original_cost: Optional[float]) -> Optional[float]:
    """
    Definition: ((Anticipated Cost - Original Cost) / Original Cost) * 100
    Null Behavior: Returns None if either is None, or if original_cost is 0.
    """
    if _is_missing(anticipated_cost) or _is_missing(original_cost) or original_cost == 0:
        return None
    return round(((anticipated_cost - original_cost) / original_cost) * 100, 2)

def compute_schedule_delay_months(anticipated_completion_date: str, original_completion_date: str) -> Optional[float]:
    """
    Definition: Anticipated Completion Date - Original Completion Date in months.
    Null Behavior: Returns None if either is None or invalid date.
    Returns 0.0 if completed early or on time.
    """
    if _is_missing(anticipated_completion_date) or _is_missing(original_completion_date):
        return None
        
    try:
        a_date = pd.to_datetime(anticipated_completion_date)
        o_date = pd.to_datetime(original_completion_date)
        
        diff = relativedelta(a_date, o_date)
        delay = diff.years * 12 + diff.months + (1 if diff.days > 15 else 0)
        return float(max(0, delay))
    except Exception:
        return None

def compute_time_elapsed_pct(report_date_str: Optional[str], start_date_str: Optional[str], original_date_str: Optional[str]) -> Optional[float]:
    """
    Definition: ((Report Date - Start Date) / (Original Completion - Start Date)) * 100
    Bounded between 0 and 100.
    """
    if not report_date_str or not start_date_str or not original_date_str:
        return None
    try:
        report = datetime.datetime.strptime(report_date_str, "%Y-%m-%d")
        start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end = datetime.datetime.strptime(original_date_str, "%Y-%m-%d")
        
        total_days = (end - start).days
        if total_days <= 0:
            return None
            
        elapsed_days = (report - start).days
        pct = (elapsed_days / total_days) * 100
        return round(max(0.0, min(100.0, pct)), 2)
    except Exception:
        return None
