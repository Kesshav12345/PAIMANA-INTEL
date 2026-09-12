import sqlite3
import pandas as pd
from pathlib import Path
from dateutil import parser

# We use the new data directories
WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"

def safe_parse_date(d_str):
    """Safely parse date strings."""
    if pd.isna(d_str) or not d_str: return None
    try:
        return parser.parse(d_str, dayfirst=True)
    except:
        return None

def compute_cost_overrun_pct(original, anticipated):
    """
    Computation ID: COMP_001
    Name: Cost Overrun Percentage
    Formula: ((Anticipated - Original) / Original) * 100
    Null behavior: Returns None if Original <= 0 or if inputs are missing.
    """
    if pd.isna(original) or pd.isna(anticipated): return None
    if original <= 0: return None
    return ((anticipated - original) / original) * 100

def compute_financial_progress_pct(expenditure, original, revised, anticipated):
    """
    Computation ID: COMP_002
    Name: Financial Progress Percentage
    Formula: (Cumulative Expenditure / Baseline Cost) * 100
    Baseline Cost: Anticipated if available, else Revised, else Original.
    """
    if pd.isna(expenditure): return None
    baseline = anticipated if not pd.isna(anticipated) else (revised if not pd.isna(revised) else original)
    if pd.isna(baseline) or baseline <= 0: return None
    return (expenditure / baseline) * 100

def compute_schedule_delay_months(original_date, anticipated_date):
    """
    Computation ID: COMP_003
    Name: Schedule Delay (Months)
    Formula: Months between original completion date and anticipated completion date.
    """
    if not original_date or not anticipated_date: return None
    return (anticipated_date.year - original_date.year) * 12 + (anticipated_date.month - original_date.month)

def compute_time_elapsed_pct(approval_date, original_date, report_date):
    """
    Computation ID: COMP_004
    Name: Time Elapsed Percentage
    Formula: (Elapsed Days / Total Planned Days) * 100
    """
    if not approval_date or not original_date or not report_date: return None
    if original_date <= approval_date: return None
    total_days = (original_date - approval_date).days
    elapsed = (report_date - approval_date).days
    pct = (elapsed / total_days) * 100
    return max(0, pct)

def compute_and_load_derived_features():
    """Extracts raw canonical facts, computes derived analytics, and saves to DB."""
    conn = sqlite3.connect(DB_PATH)
    
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
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Error querying database: {e}")
        conn.close()
        return
        
    if df.empty:
        print("No canonical data found.")
        conn.close()
        return

    # Parse dates safely
    df['doa_dt'] = df['Date_of_Approval'].apply(safe_parse_date)
    df['ocd_dt'] = df['Original_Completion_Date'].apply(safe_parse_date)
    df['acd_dt'] = df['Anticipated_Completion_Date'].apply(safe_parse_date)
    df['rep_dt'] = df['Report_Date'].apply(safe_parse_date)
    
    derived_records = []
    
    for _, row in df.iterrows():
        obs_sk = row['Observation_SK']
        
        cost_overrun = compute_cost_overrun_pct(row['Original_Cost'], row['Anticipated_Cost'])
        fin_prog = compute_financial_progress_pct(row['Cumulative_Expenditure'], row['Original_Cost'], row['Revised_Cost'], row['Anticipated_Cost'])
        delay_months = compute_schedule_delay_months(row['ocd_dt'], row['acd_dt'])
        time_elapsed = compute_time_elapsed_pct(row['doa_dt'], row['ocd_dt'], row['rep_dt'])
        
        derived_records.append({
            "Observation_SK": obs_sk,
            "Cost_Overrun_Pct": cost_overrun,
            "Financial_Progress_Pct": fin_prog,
            "Schedule_Delay_Months": delay_months,
            "Time_Elapsed_Pct": time_elapsed
        })
        
    # Write to Fact_Project_Derived
    derived_df = pd.DataFrame(derived_records)
    # Using 'replace' for simplicity, though dropping/creating is safer. SQLite handles this well.
    derived_df.to_sql("Fact_Project_Derived", conn, if_exists="replace", index=False)
    
    # Add unique constraints to Fact_Project_Derived if we were defining it via DDL, 
    # but pandas to_sql doesn't let us specify complex DDL. 
    # Since we replaced the table, it's 1:1 with Observation_SK.
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_derived_obs ON Fact_Project_Derived(Observation_SK);")
    except Exception:
        pass
        
    conn.commit()
    conn.close()
    print(f"Analytical computations complete. Saved {len(derived_df)} derived records.")

if __name__ == "__main__":
    compute_and_load_derived_features()
