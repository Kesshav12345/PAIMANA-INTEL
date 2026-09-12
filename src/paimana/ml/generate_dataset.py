import sqlite3
import pandas as pd
from pathlib import Path
from dateutil import parser
import numpy as np

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"
ML_OUTPUT_PATH = WORKSPACE / "data" / "ml" / "ML_DATASET.csv"

def generate_ml_dataset():
    """Generates a point-in-time safe ML dataset."""
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Base query for features (known at time T)
    feature_query = """
    SELECT 
        o.Observation_SK,
        p.Project_SK,
        p.Project_Code,
        p.Project_Name,
        r.Report_Date,
        o.Original_Cost,
        o.Revised_Cost,
        o.Anticipated_Cost,
        o.Cumulative_Expenditure,
        d.Financial_Progress_Pct,
        d.Time_Elapsed_Pct,
        d.Schedule_Delay_Months,
        o.Physical_Progress_Pct
    FROM Fact_Project_Observation o
    JOIN Fact_Project_Derived d ON o.Observation_SK = d.Observation_SK
    JOIN Dim_Project p ON o.Project_SK = p.Project_SK
    JOIN Dim_Report r ON o.Report_SK = r.Report_SK
    """
    
    df = pd.read_sql_query(feature_query, conn)
    
    if df.empty:
        print("Error: No data available for ML generation.")
        conn.close()
        return

    # Parse report dates for temporal logic
    def parse_dt(d):
        try: return parser.parse(d, dayfirst=True)
        except: return pd.NaT
        
    df['Report_DT'] = df['Report_Date'].apply(parse_dt)
    
    # Sort for temporal processing
    df = df.sort_values(by=['Project_SK', 'Report_DT'])
    
    # 2. Target Generation (Future Horizon = 6 Months)
    # We want to predict if the project will be delayed (Schedule_Delay_Months > 0) 6 months from now.
    # To do this safely, we merge the dataframe with itself, shifted by 6 months.
    
    future_records = []
    
    for project_sk, group in df.groupby('Project_SK'):
        group = group.reset_index(drop=True)
        for i, row in group.iterrows():
            current_date = row['Report_DT']
            if pd.isna(current_date):
                continue
                
            # Find ANY future record after the current date
            future_obs = group[group['Report_DT'] > current_date]
            
            target_delayed = np.nan # Use NaN for missing labels (censoring)
            if not future_obs.empty:
                # If there are multiple future obs, see if ANY have a delay
                any_delay = (future_obs['Schedule_Delay_Months'] > 0).any()
                target_delayed = 1 if any_delay else 0
                    
            record = row.to_dict()
            record['Target_Delayed_6M'] = target_delayed
            future_records.append(record)
            
    ml_df = pd.DataFrame(future_records)
    
    # Impute missing features for baseline model compatibility
    ml_df['Financial_Progress_Pct'] = ml_df['Financial_Progress_Pct'].fillna(0)
    ml_df['Time_Elapsed_Pct'] = ml_df['Time_Elapsed_Pct'].fillna(0)
    ml_df['Schedule_Delay_Months'] = ml_df['Schedule_Delay_Months'].fillna(0)
    ml_df['Physical_Progress_Pct'] = ml_df['Physical_Progress_Pct'].fillna(0)
    
    # Drop rows where target is NaN (we can't train on censored data)
    valid_ml_df = ml_df.dropna(subset=['Target_Delayed_6M'])
    
    # Drop datetime object before saving
    valid_ml_df = valid_ml_df.drop(columns=['Report_DT'])
    
    ML_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    valid_ml_df.to_csv(ML_OUTPUT_PATH, index=False)
    
    print(f"ML dataset generated successfully.")
    print(f"Total Rows Generated (Features): {len(ml_df)}")
    print(f"Valid Rows for Training (Uncensored Target): {len(valid_ml_df)}")
    print(f"Saved to {ML_OUTPUT_PATH}")
    
    conn.close()

if __name__ == "__main__":
    generate_ml_dataset()
