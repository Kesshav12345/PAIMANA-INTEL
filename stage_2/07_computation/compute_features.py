import sqlite3
import pandas as pd
from pathlib import Path
from dateutil import parser
import datetime

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "stage_2" / "05_canonical" / "paimana_analytical.db"

def safe_parse_date(d_str):
    if not d_str: return None
    try:
        return parser.parse(d_str, dayfirst=True)
    except:
        return None

def compute_features():
    conn = sqlite3.connect(DB_PATH)
    
    # Extract canonical facts
    query = """
    SELECT 
        o.Observation_SK,
        p.Project_SK,
        p.Date_of_Approval,
        o.Original_Cost,
        o.Revised_Cost,
        o.Anticipated_Cost,
        o.Cumulative_Expenditure,
        o.Original_Completion_Date,
        o.Revised_Completion_Date,
        o.Anticipated_Completion_Date,
        r.Report_Date
    FROM Fact_Project_Observation o
    JOIN Dim_Project p ON o.Project_SK = p.Project_SK
    JOIN Dim_Report r ON o.Report_SK = r.Report_SK
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No canonical data found. Run the canonical load step first.")
        return
        
    derived_records = []
    
    for _, row in df.iterrows():
        doa = safe_parse_date(row['Date_of_Approval'])
        ocd = safe_parse_date(row['Original_Completion_Date'])
        rcd = safe_parse_date(row['Revised_Completion_Date'])
        acd = safe_parse_date(row['Anticipated_Completion_Date'])
        rep_date = safe_parse_date(row['Report_Date'])
        
        orig_cost = row['Original_Cost']
        rev_cost = row['Revised_Cost']
        ant_cost = row['Anticipated_Cost']
        expenditure = row['Cumulative_Expenditure']
        
        # Computations
        cost_overrun_pct = None
        if ant_cost and orig_cost and orig_cost > 0:
            cost_overrun_pct = ((ant_cost - orig_cost) / orig_cost) * 100
            
        financial_progress_pct = None
        # Use anticipated cost as the denominator if available, else revised, else original
        baseline_cost = ant_cost if ant_cost else (rev_cost if rev_cost else orig_cost)
        if expenditure and baseline_cost and baseline_cost > 0:
            financial_progress_pct = (expenditure / baseline_cost) * 100
            
        schedule_delay_months = None
        if acd and ocd:
            schedule_delay_months = (acd.year - ocd.year) * 12 + (acd.month - ocd.month)
            
        time_elapsed_pct = None
        if doa and ocd and rep_date and (ocd > doa):
            total_duration_days = (ocd - doa).days
            elapsed_days = (rep_date - doa).days
            time_elapsed_pct = (elapsed_days / total_duration_days) * 100
            if time_elapsed_pct < 0: time_elapsed_pct = 0
            
        derived_records.append({
            "Observation_SK": row['Observation_SK'],
            "Cost_Overrun_Pct": cost_overrun_pct,
            "Financial_Progress_Pct": financial_progress_pct,
            "Schedule_Delay_Months": schedule_delay_months,
            "Time_Elapsed_Pct": time_elapsed_pct
        })
        
    # Write to a new derived table in SQLite
    derived_df = pd.DataFrame(derived_records)
    derived_df.to_sql("Fact_Project_Derived", conn, if_exists="replace", index=False)
    
    conn.close()
    print(f"Computations complete. Fact_Project_Derived table created with {len(derived_df)} rows.")

if __name__ == "__main__":
    compute_features()
