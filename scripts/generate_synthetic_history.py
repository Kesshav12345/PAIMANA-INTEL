import sqlite3
import pandas as pd
from pathlib import Path
import random
import uuid
import datetime
from dateutil.relativedelta import relativedelta

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"

def generate_history():
    print(f"Connecting to {DB_PATH} to generate synthetic history...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all projects
    projects = pd.read_sql_query("SELECT Project_SK FROM Dim_Project", conn)
    if projects.empty:
        print("No projects found. Please run the canonical DB load first.")
        return
        
    print(f"Found {len(projects)} projects. Simulating 120 months (10 years) of history for each.")
    
    # First, let's create 120 synthetic reports going back from Jan 2026
    start_date = datetime.date(2016, 1, 1)
    report_sks = []
    
    for i in range(120):
        r_date = start_date + relativedelta(months=i)
        r_date_str = r_date.strftime("%B %Y")
        report_sk = f"SYNTH_{r_date.strftime('%Y%m')}"
        
        cursor.execute("""
            INSERT OR IGNORE INTO Dim_Report 
            (Report_SK, Report_Type, Report_Date, Source_File_Name, Source_File_Hash)
            VALUES (?, ?, ?, ?, ?)
        """, (report_sk, "SYNTHETIC_FLASH_REPORT", r_date_str, f"Synthetic_{report_sk}.pdf", str(uuid.uuid4())))
        
        report_sks.append((report_sk, r_date))
        
    # Now simulate project observations
    observations = []
    for _, row in projects.iterrows():
        p_sk = row['Project_SK']
        
        # Base project parameters
        original_cost = round(random.uniform(150.0, 5000.0), 2)
        revised_cost = original_cost
        anticipated_cost = original_cost
        
        original_completion = start_date + relativedelta(months=random.randint(36, 72))
        revised_completion = original_completion
        anticipated_completion = original_completion
        
        cumulative_expenditure = 0.0
        physical_progress = 0.0
        
        for r_sk, r_date in report_sks:
            # Monthly increment in expenditure and progress
            expenditure_increment = random.uniform(0.0, 20.0)
            cumulative_expenditure += expenditure_increment
            if cumulative_expenditure > anticipated_cost:
                cumulative_expenditure = anticipated_cost
                
            phys_increment = random.uniform(0.0, 1.5)
            physical_progress += phys_increment
            if physical_progress > 100.0:
                physical_progress = 100.0
                
            # Random cost overrun event (5% chance per month)
            if random.random() < 0.05:
                anticipated_cost += round(random.uniform(50.0, 300.0), 2)
                
            # Random schedule delay event (5% chance per month)
            if random.random() < 0.05:
                anticipated_completion += relativedelta(months=random.randint(3, 12))
                
            observations.append({
                "Project_SK": p_sk,
                "Report_SK": r_sk,
                "Original_Cost": original_cost,
                "Revised_Cost": revised_cost if revised_cost != original_cost else None,
                "Anticipated_Cost": anticipated_cost,
                "Cumulative_Expenditure": cumulative_expenditure,
                "Physical_Progress_Pct": physical_progress,
                "Original_Completion_Date": original_completion.strftime("%Y-%m-%d"),
                "Revised_Completion_Date": revised_completion.strftime("%Y-%m-%d") if revised_completion != original_completion else None,
                "Anticipated_Completion_Date": anticipated_completion.strftime("%Y-%m-%d")
            })
            
    # Insert observations
    obs_df = pd.DataFrame(observations)
    for _, obs in obs_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO Fact_Project_Observation
            (Project_SK, Report_SK, Original_Cost, Revised_Cost, Anticipated_Cost, 
             Cumulative_Expenditure, Physical_Progress_Pct, Original_Completion_Date, 
             Revised_Completion_Date, Anticipated_Completion_Date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obs['Project_SK'], obs['Report_SK'], obs['Original_Cost'], obs['Revised_Cost'], obs['Anticipated_Cost'],
            obs['Cumulative_Expenditure'], obs['Physical_Progress_Pct'], obs['Original_Completion_Date'],
            obs['Revised_Completion_Date'], obs['Anticipated_Completion_Date']
        ))
        
    conn.commit()
    conn.close()
    
    print(f"Synthetic history generation complete. Inserted {len(obs_df)} observations.")

if __name__ == "__main__":
    generate_history()
