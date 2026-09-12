import sqlite3
import pandas as pd
from pathlib import Path

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "stage_2" / "05_canonical" / "paimana_analytical.db"
ML_OUTPUT_PATH = WORKSPACE / "stage_2" / "09_ml" / "ML_DATASET.csv"

def generate_ml_dataset():
    conn = sqlite3.connect(DB_PATH)
    
    # ML Dataset requires point-in-time safety. We join Fact_Project_Observation with Fact_Project_Derived
    # and Dim_Project. Target: "Will this project's anticipated cost increase in the next 6 months?"
    # Since we only have ~15 months of data, we will just create a basic classification target:
    # Target: Has Schedule Delay > 0 (1) or not (0)
    
    query = """
    SELECT 
        o.Observation_SK,
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
        CASE WHEN d.Schedule_Delay_Months > 0 THEN 1 ELSE 0 END as Target_Is_Delayed
    FROM Fact_Project_Observation o
    JOIN Fact_Project_Derived d ON o.Observation_SK = d.Observation_SK
    JOIN Dim_Project p ON o.Project_SK = p.Project_SK
    JOIN Dim_Report r ON o.Report_SK = r.Report_SK
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        df.to_csv(ML_OUTPUT_PATH, index=False)
        print(f"ML dataset generated successfully with {len(df)} rows and {len(df.columns)} features.")
        print(f"Saved to {ML_OUTPUT_PATH}")
    except Exception as e:
        print(f"Failed to generate ML dataset: {e}")
        
    conn.close()

if __name__ == "__main__":
    generate_ml_dataset()
