import pandas as pd
import numpy as np
from pathlib import Path
from paimana.analytics.derive import derive_analytics

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DATA_PATH = WORKSPACE / "data" / "ml" / "ML_DATASET.csv"

def build_schedule_delay_label(group, current_date):
    """
    Constructs a future label: 1 if ANY observation strictly after current_date
    has a Schedule_Delay_Months > 0, else 0.
    Returns np.nan if there are no future observations (censored).
    """
    future_obs = group[group['Report_Date'] > current_date]
    if future_obs.empty:
        return np.nan
        
    any_delay = (future_obs['Schedule_Delay_Months'] > 0).any()
    return 1.0 if any_delay else 0.0

def generate_ml_dataset():
    """Generates Point-in-Time safe ML features and labels."""
    if not DATA_PATH.parent.exists():
        DATA_PATH.parent.mkdir(parents=True)
        
    # Get all derived features for all time
    df = derive_analytics()
    if df.empty:
        print("No data available to build ML dataset.")
        return
        
    df['Report_Date'] = pd.to_datetime(df['Report_Date'])
    
    # Sort chronologically
    df = df.sort_values(by=['Project_SK', 'Report_Date'])
    
    records = []
    
    # Group by project to compute temporal features and future targets
    for p_sk, group in df.groupby('Project_SK'):
        for idx, row in group.iterrows():
            current_date = row['Report_Date']
            
            # Label Construction (Strictly Future)
            target_delayed = build_schedule_delay_label(group, current_date)
            
            # Point in Time Features (Strictly Past/Current)
            # We must NOT include the target Schedule_Delay_Months in the features directly!
            
            record = {
                'Project_SK': p_sk,
                'Report_SK': row['Report_SK'],
                'Report_Date': current_date,
                
                # Base Features
                'Original_Cost': row['Original_Cost'],
                'Revised_Cost': row['Revised_Cost'],
                'Cumulative_Expenditure': row['Cumulative_Expenditure'],
                'Physical_Progress_Pct': row['Physical_Progress_Pct'],
                'Financial_Progress_Pct': row['Financial_Progress_Pct'],
                'Physical_Financial_Divergence': row['Physical_Financial_Divergence'],
                
                # Target
                'Target_Delayed_Future': target_delayed
            }
            records.append(record)
            
    ml_df = pd.DataFrame(records)
    
    # Drop rows where target is NaN (censored)
    valid_ml_df = ml_df.dropna(subset=['Target_Delayed_Future'])
    
    valid_ml_df.to_csv(DATA_PATH, index=False)
    print(f"ML dataset generated successfully. {len(valid_ml_df)} valid training rows.")

if __name__ == "__main__":
    generate_ml_dataset()
