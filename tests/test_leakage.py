import pytest
import pandas as pd
from paimana.ml.generator import build_schedule_delay_label

def test_target_horizon_strictness():
    """
    Ensures that the ML target ONLY looks 6 months ahead, 
    and does NOT leak information from 12 months ahead,
    and returns NaN if the horizon is censored.
    """
    data = [
        {'Report_Date': '2025-01-01', 'Schedule_Delay_Months': 0},
        {'Report_Date': '2025-04-01', 'Schedule_Delay_Months': 0}, # Within 6M (No delay)
        {'Report_Date': '2025-09-01', 'Schedule_Delay_Months': 5}, # Outside 6M (Delayed)
    ]
    df = pd.DataFrame(data)
    df['Report_Date'] = pd.to_datetime(df['Report_Date'])
    
    # 1. Evaluate from 2025-01-01
    # Horizon is up to 2025-07-01. The only future obs in horizon is 2025-04-01 (Delay=0)
    # The 2025-09-01 delay MUST NOT trigger the label!
    label = build_schedule_delay_label(df, '2025-01-01')
    assert label == 0.0, "Leakage: Target saw a delay outside the 6-month horizon!"
    
    # 2. Evaluate from 2025-04-01
    # Horizon is up to 2025-10-01. Future obs is 2025-09-01 (Delay=5)
    # This SHOULD trigger the label.
    label2 = build_schedule_delay_label(df, '2025-04-01')
    assert label2 == 1.0, "Target failed to detect delay within the horizon."
    
    # 3. Evaluate from 2025-09-01
    # No future observations exist.
    # MUST return NaN (Censored)
    label3 = build_schedule_delay_label(df, '2025-09-01')
    assert pd.isna(label3), "Failed to censor project with missing future observations."
