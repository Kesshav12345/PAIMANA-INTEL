import sqlite3
import json
from pathlib import Path
import csv

# We use the new data directories
WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"
IDENTITY_JSON_DIR = WORKSPACE / "stage_2" / "04_identity" / "resolved_json"
MANIFEST_PATH = WORKSPACE / "stage_2" / "01_raw" / "SOURCE_MANIFEST.csv"
IDENTITY_REPORT = WORKSPACE / "stage_2" / "04_identity" / "IDENTITY_RESOLUTION.csv"

# Added UNIQUE constraints and analytical views
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
    FOREIGN KEY(Report_SK) REFERENCES Dim_Report(Report_SK),
    UNIQUE(Project_SK, Report_SK)
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

-- Analytical Views for Backend
CREATE VIEW IF NOT EXISTS View_Current_Project_Status AS
SELECT 
    p.Project_SK,
    p.PAIMANA_ID,
    p.Project_Code,
    p.Project_Name,
    p.Date_of_Approval,
    r.Report_Date AS Latest_Report_Date,
    o.Original_Cost,
    o.Anticipated_Cost,
    o.Cumulative_Expenditure,
    o.Physical_Progress_Pct,
    o.Original_Completion_Date,
    o.Anticipated_Completion_Date
FROM Dim_Project p
JOIN Fact_Project_Observation o ON p.Project_SK = o.Project_SK
JOIN Dim_Report r ON o.Report_SK = r.Report_SK
WHERE r.Report_Date = (
    SELECT MAX(r2.Report_Date)
    FROM Fact_Project_Observation o2
    JOIN Dim_Report r2 ON o2.Report_SK = r2.Report_SK
    WHERE o2.Project_SK = p.Project_SK
);

CREATE VIEW IF NOT EXISTS View_Project_Timeline AS
SELECT 
    p.Project_SK,
    p.Project_Name,
    r.Report_Date,
    o.Original_Cost,
    o.Anticipated_Cost,
    o.Cumulative_Expenditure,
    o.Physical_Progress_Pct
FROM Fact_Project_Observation o
JOIN Dim_Project p ON o.Project_SK = p.Project_SK
JOIN Dim_Report r ON o.Report_SK = r.Report_SK
ORDER BY p.Project_SK, r.Report_Date;
"""

def load_canonical():
    # Ensure canonical directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Initialize schema
    cursor.executescript(SCHEMA_SQL)
    
    # Clear existing data for idempotency
    cursor.execute("DELETE FROM Fact_Project_Observation")
    cursor.execute("DELETE FROM Fact_Sector_Performance")
    cursor.execute("DELETE FROM Dim_Project")
    cursor.execute("DELETE FROM Dim_Report")
    
    # 2. Load Reports
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['duplicate_group']: continue # Skip duplicates
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
                    INSERT OR IGNORE INTO Dim_Project
                    (Project_SK, PAIMANA_ID, Project_Code, Project_Name, Date_of_Approval)
                    VALUES (?, ?, ?, ?, ?)
                """, (row.get('Project_SK'), row.get('PAIMANA_ID'), row.get('Project_Code'), row.get('Original_Name_Sample'), None))
    
    # 4. Load Facts
    if IDENTITY_JSON_DIR.exists():
        for json_file in IDENTITY_JSON_DIR.glob("*_std.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    records = json.load(f)
                except:
                    continue
                
            for r in records:
                if r.get('grain') == 'PROJECT_OBSERVATION':
                    if r.get('date_of_approval'):
                        cursor.execute("UPDATE Dim_Project SET Date_of_Approval = ? WHERE Project_SK = ?", (r['date_of_approval'], r['project_sk']))
                        
                    cursor.execute("""
                        INSERT OR IGNORE INTO Fact_Project_Observation
                        (Project_SK, Report_SK, Original_Cost, Revised_Cost, Anticipated_Cost, 
                         Cumulative_Expenditure, Physical_Progress_Pct, Original_Completion_Date, 
                         Revised_Completion_Date, Anticipated_Completion_Date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r.get('project_sk'), r.get('source_id'), r.get('original_cost'), r.get('revised_cost'), r.get('anticipated_cost'),
                        r.get('cumulative_expenditure'), r.get('physical_progress_pct'), r.get('original_completion_date'),
                        r.get('revised_completion_date'), r.get('anticipated_completion_date')
                    ))
                elif r.get('grain') == 'SECTOR_PERFORMANCE':
                    cursor.execute("""
                        INSERT OR IGNORE INTO Fact_Sector_Performance
                        (Report_SK, Metric_Name, Metric_Unit, Achievement_Value, Target_Value, Previous_Year_Value, Growth_Pct_YoY)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r.get('source_id'), r.get('metric_name'), r.get('metric_unit'), r.get('achievement_value'), r.get('target_value'), r.get('previous_year_value'), r.get('growth_pct_yoy')
                    ))
                
    conn.commit()
    conn.close()
    print(f"Database loaded successfully at {DB_PATH}")

if __name__ == "__main__":
    load_canonical()
