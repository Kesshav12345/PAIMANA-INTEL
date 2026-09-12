import sqlite3
import pandas as pd
from pathlib import Path
from paimana.formulas.registry import (
    compute_financial_progress,
    compute_cost_overrun_amount,
    compute_cost_overrun_pct,
    compute_schedule_delay_months
)

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"

def derive_analytics():
    """Reads Fact_Project_Observation, applies deterministic formulas, and returns a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        o.Project_SK, o.Report_SK, r.Report_Date,
        o.Original_Cost, o.Revised_Cost, o.Anticipated_Cost, o.Cumulative_Expenditure, o.Physical_Progress_Pct,
        o.Original_Completion_Date, o.Revised_Completion_Date, o.Anticipated_Completion_Date
    FROM Fact_Project_Observation o
    JOIN Dim_Report r ON o.Report_SK = r.Report_SK
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No observation data found.")
        return df
        
    # Apply formulas
    df['Financial_Progress_Pct'] = df.apply(
        lambda row: compute_financial_progress(row['Cumulative_Expenditure'], row['Anticipated_Cost']), 
        axis=1
    )
    
    df['Cost_Overrun_Amount'] = df.apply(
        lambda row: compute_cost_overrun_amount(row['Anticipated_Cost'], row['Original_Cost']),
        axis=1
    )
    
    df['Cost_Overrun_Pct'] = df.apply(
        lambda row: compute_cost_overrun_pct(row['Anticipated_Cost'], row['Original_Cost']),
        axis=1
    )
    
    df['Schedule_Delay_Months'] = df.apply(
        lambda row: compute_schedule_delay_months(row['Anticipated_Completion_Date'], row['Original_Completion_Date']),
        axis=1
    )
    
    # Calculate Physical-Financial Divergence
    df['Physical_Financial_Divergence'] = df.apply(
        lambda row: round(row['Physical_Progress_Pct'] - row['Financial_Progress_Pct'], 2)
        if pd.notna(row['Physical_Progress_Pct']) and pd.notna(row['Financial_Progress_Pct']) else None,
        axis=1
    )
    
    print(f"Successfully derived metrics for {len(df)} observations.")
    return df

if __name__ == "__main__":
    derived_df = derive_analytics()
    if not derived_df.empty:
        print(derived_df[['Project_SK', 'Cost_Overrun_Pct', 'Schedule_Delay_Months']].head())
