import sqlite3
import json
from pathlib import Path
import csv

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "stage_2" / "05_canonical" / "paimana_analytical.db"
IDENTITY_JSON_DIR = WORKSPACE / "stage_2" / "04_identity" / "resolved_json"
MANIFEST_PATH = WORKSPACE / "stage_2" / "01_raw" / "SOURCE_MANIFEST.csv"
IDENTITY_REPORT = WORKSPACE / "stage_2" / "04_identity" / "IDENTITY_RESOLUTION.csv"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS Dim_Report (
    Report_SK TEXT PRIMARY KEY,
    Report_Type TEXT,
    Report_Date TEXT,
    Source_File_Name TEXT,
    Source_File_Hash TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Project (
    Project_SK INTEGER PRIMARY KEY,
    PAIMANA_ID TEXT,
    Project_Code TEXT,
    Project_Name TEXT,
    Date_of_Approval TEXT
);

CREATE TABLE IF NOT EXISTS Fact_Project_Observation (
    Observation_SK INTEGER PRIMARY KEY AUTOINCREMENT,
    Project_SK INTEGER,
    Report_SK TEXT,
    Original_Cost REAL,
    Revised_Cost REAL,
    Anticipated_Cost REAL,
    Cumulative_Expenditure REAL,
    Physical_Progress_Pct REAL,
    Original_Completion_Date TEXT,
    Revised_Completion_Date TEXT,
    Anticipated_Completion_Date TEXT,
    FOREIGN KEY(Project_SK) REFERENCES Dim_Project(Project_SK),
    FOREIGN KEY(Report_SK) REFERENCES Dim_Report(Report_SK)
);

CREATE TABLE IF NOT EXISTS Fact_Sector_Performance (
    Observation_SK INTEGER PRIMARY KEY AUTOINCREMENT,
    Report_SK TEXT,
    Metric_Name TEXT,
    Metric_Unit TEXT,
    Achievement_Value REAL,
    Target_Value REAL,
    Previous_Year_Value REAL,
    Growth_Pct_YoY REAL,
    FOREIGN KEY(Report_SK) REFERENCES Dim_Report(Report_SK)
);
"""

def load_canonical():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Initialize schema
    cursor.executescript(SCHEMA_SQL)
    
    # Clear existing data (Idempotent load)
    cursor.execute("DELETE FROM Fact_Project_Observation")
    cursor.execute("DELETE FROM Fact_Sector_Performance")
    cursor.execute("DELETE FROM Dim_Project")
    cursor.execute("DELETE FROM Dim_Report")
    
    # 2. Load Reports
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['duplicate_group']: continue # Just skip duplicates when inserting into Dim_Report to avoid clutter
            cursor.execute("""
                INSERT OR IGNORE INTO Dim_Report 
                (Report_SK, Report_Type, Report_Date, Source_File_Name, Source_File_Hash)
                VALUES (?, ?, ?, ?, ?)
            """, (row['source_id'], row['report_type'], row['report_date'], row['filename'], row['content_hash']))
            
    # 3. Load Projects
    if IDENTITY_REPORT.exists():
        with open(IDENTITY_REPORT, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT OR REPLACE INTO Dim_Project
                    (Project_SK, PAIMANA_ID, Project_Code, Project_Name, Date_of_Approval)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['Project_SK'], row['PAIMANA_ID'], row['Project_Code'], row['Original_Name_Sample'], None))
    
    # 4. Load Facts
    for json_file in IDENTITY_JSON_DIR.glob("*_std.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
            
        for r in records:
            if r['grain'] == 'PROJECT_OBSERVATION':
                # Update approval date if found
                if r.get('date_of_approval'):
                    cursor.execute("UPDATE Dim_Project SET Date_of_Approval = ? WHERE Project_SK = ?", (r['date_of_approval'], r['project_sk']))
                    
                cursor.execute("""
                    INSERT INTO Fact_Project_Observation
                    (Project_SK, Report_SK, Original_Cost, Revised_Cost, Anticipated_Cost, 
                     Cumulative_Expenditure, Physical_Progress_Pct, Original_Completion_Date, 
                     Revised_Completion_Date, Anticipated_Completion_Date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r['project_sk'], r['source_id'], r['original_cost'], r['revised_cost'], r['anticipated_cost'],
                    r['cumulative_expenditure'], r['physical_progress_pct'], r['original_completion_date'],
                    r['revised_completion_date'], r['anticipated_completion_date']
                ))
            elif r['grain'] == 'SECTOR_PERFORMANCE':
                cursor.execute("""
                    INSERT INTO Fact_Sector_Performance
                    (Report_SK, Metric_Name, Metric_Unit, Achievement_Value, Target_Value, Previous_Year_Value, Growth_Pct_YoY)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    r['source_id'], r['metric_name'], r['metric_unit'], r['achievement_value'], r['target_value'], r['previous_year_value'], r['growth_pct_yoy']
                ))
                
    conn.commit()
    conn.close()
    print(f"Database loaded successfully at {DB_PATH}")

if __name__ == "__main__":
    load_canonical()
