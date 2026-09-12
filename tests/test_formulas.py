import pytest
import numpy as np
from paimana.formulas.registry import (
    compute_cost_overrun_pct,
    compute_schedule_delay_months,
    compute_financial_progress
)

def test_cost_overrun_normal():
    assert compute_cost_overrun_pct(150.0, 100.0) == 50.0
    assert compute_cost_overrun_pct(100.0, 100.0) == 0.0

def test_cost_overrun_zero_denominator():
    assert compute_cost_overrun_pct(150.0, 0.0) is None

def test_cost_overrun_missing_values():
    assert compute_cost_overrun_pct(None, 100.0) is None
    assert compute_cost_overrun_pct(150.0, None) is None
    assert compute_cost_overrun_pct(np.nan, 100.0) is None

def test_financial_progress():
    assert compute_financial_progress(50.0, 100.0) == 50.0
    assert compute_financial_progress(0.0, 100.0) == 0.0
    assert compute_financial_progress(150.0, 0.0) is None

def test_schedule_delay_months():
    # Normal case
    assert compute_schedule_delay_months("2025-06-01", "2025-01-01") == 5.0
    # No delay (on time)
    assert compute_schedule_delay_months("2025-01-01", "2025-01-01") == 0.0
    # Early completion
    assert compute_schedule_delay_months("2024-12-01", "2025-01-01") == 0.0
    # Missing date
    assert compute_schedule_delay_months(None, "2025-01-01") is None
    # Invalid date string
    assert compute_schedule_delay_months("invalid", "2025-01-01") is None
