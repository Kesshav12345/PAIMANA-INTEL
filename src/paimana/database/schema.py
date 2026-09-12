import sqlite3
from pathlib import Path
import json
import csv
from paimana.config import CANONICAL_DB_PATH, STAGE_2_IDENTITY_JSON_DIR, STAGE_2_MANIFEST_PATH, STAGE_2_IDENTITY_REPORT

SCHEMA_SQL = """
-- DIMENSIONS
CREATE TABLE IF NOT EXISTS Dim_Project (
    Project_SK INTEGER PRIMARY KEY,
    Original_Project_Name TEXT,
    Sector TEXT,
    Ministry TEXT,
    State TEXT,
    Date_of_Approval TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Report (
    Report_SK TEXT PRIMARY KEY,
    Report_Type TEXT,
    Report_Date TEXT,
    Source_File_Name TEXT,
    Source_File_Hash TEXT
);

-- FACTS
CREATE TABLE IF NOT EXISTS Fact_Project_Observation (
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
    
    -- Explicit grain constraint
    PRIMARY KEY (Project_SK, Report_SK),
    FOREIGN KEY (Project_SK) REFERENCES Dim_Project(Project_SK),
    FOREIGN KEY (Report_SK) REFERENCES Dim_Report(Report_SK)
);

CREATE TABLE IF NOT EXISTS Fact_Project_Warning (
    Warning_SK INTEGER PRIMARY KEY AUTOINCREMENT,
    Project_SK INTEGER,
    Report_SK TEXT,
    Warning_Type TEXT,
    Severity TEXT,
    Trigger_Date TEXT,
    FOREIGN KEY (Project_SK) REFERENCES Dim_Project(Project_SK)
);

CREATE TABLE IF NOT EXISTS Fact_Project_Event (
    Event_SK INTEGER PRIMARY KEY AUTOINCREMENT,
    Project_SK INTEGER,
    Report_SK TEXT,
    Event_Type TEXT,
    Event_Description TEXT,
    Event_Date TEXT,
    FOREIGN KEY (Project_SK) REFERENCES Dim_Project(Project_SK)
);

-- ANALYTICAL VIEWS
CREATE VIEW IF NOT EXISTS View_Current_Project_Status AS
SELECT 
    p.Project_SK, p.Original_Project_Name, p.Sector, p.Ministry, p.State,
    o.Original_Cost, o.Revised_Cost, o.Anticipated_Cost, o.Cumulative_Expenditure, o.Physical_Progress_Pct,
    o.Original_Completion_Date, o.Revised_Completion_Date, o.Anticipated_Completion_Date,
    r.Report_Date
FROM Dim_Project p
JOIN Fact_Project_Observation o ON p.Project_SK = o.Project_SK
JOIN Dim_Report r ON o.Report_SK = r.Report_SK
WHERE (p.Project_SK, r.Report_Date) IN (
    SELECT o_inner.Project_SK, MAX(r_inner.Report_Date)
    FROM Fact_Project_Observation o_inner
    JOIN Dim_Report r_inner ON o_inner.Report_SK = r_inner.Report_SK
    GROUP BY o_inner.Project_SK
);

CREATE VIEW IF NOT EXISTS View_Project_Timeline AS
SELECT 
    p.Project_SK, p.Original_Project_Name, r.Report_Date,
    o.Anticipated_Cost, o.Cumulative_Expenditure, o.Physical_Progress_Pct, o.Anticipated_Completion_Date
FROM Dim_Project p
JOIN Fact_Project_Observation o ON p.Project_SK = o.Project_SK
JOIN Dim_Report r ON o.Report_SK = r.Report_SK
ORDER BY p.Project_SK, r.Report_Date;

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_fact_obs_project ON Fact_Project_Observation(Project_SK);
CREATE INDEX IF NOT EXISTS idx_fact_obs_report ON Fact_Project_Observation(Report_SK);
"""

def init_db():
    if not CANONICAL_DB_PATH.parent.exists():
        CANONICAL_DB_PATH.parent.mkdir(parents=True)
        
    conn = sqlite3.connect(CANONICAL_DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript(SCHEMA_SQL)
    
    # Reset existing data (removing any synthetic data injected previously)
    cursor.execute("DELETE FROM Fact_Project_Observation")
    cursor.execute("DELETE FROM Fact_Project_Warning")
    cursor.execute("DELETE FROM Fact_Project_Event")
    cursor.execute("DELETE FROM Dim_Project")
    cursor.execute("DELETE FROM Dim_Report")
    
    # Load pure, true Stage-2 extracted data
    if STAGE_2_MANIFEST_PATH.exists():
        with open(STAGE_2_MANIFEST_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('duplicate_group'): continue
                cursor.execute("""
                    INSERT OR IGNORE INTO Dim_Report 
                    (Report_SK, Report_Type, Report_Date, Source_File_Name, Source_File_Hash)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['source_id'], row['report_type'], row['report_date'], row['filename'], row['content_hash']))
    
    if STAGE_2_IDENTITY_REPORT.exists():
        with open(STAGE_2_IDENTITY_REPORT, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT OR REPLACE INTO Dim_Project
                    (Project_SK, Original_Project_Name, Sector, Ministry, State)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['Project_SK'], row['Original_Name_Sample'], None, None, None))
                # Note: Sector/Ministry/State are derived in real data or from external sources.

    if STAGE_2_IDENTITY_JSON_DIR.exists():
        for json_file in STAGE_2_IDENTITY_JSON_DIR.glob("*_std.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
                
            for r in records:
                if r.get('grain') == 'PROJECT_OBSERVATION':
                    # Update approval date if found
                    if r.get('date_of_approval'):
                        cursor.execute("UPDATE Dim_Project SET Date_of_Approval = ? WHERE Project_SK = ?", (r['date_of_approval'], r['project_sk']))
                        
                    # Insert observation exactly as it is (no synthesis)
                    cursor.execute("""
                        INSERT OR IGNORE INTO Fact_Project_Observation
                        (Project_SK, Report_SK, Original_Cost, Revised_Cost, Anticipated_Cost, 
                         Cumulative_Expenditure, Physical_Progress_Pct, Original_Completion_Date, 
                         Revised_Completion_Date, Anticipated_Completion_Date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r['project_sk'], r['source_id'], r['original_cost'], r['revised_cost'], r['anticipated_cost'],
                        r['cumulative_expenditure'], r['physical_progress_pct'], r['original_completion_date'],
                        r['revised_completion_date'], r['anticipated_completion_date']
                    ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema successfully hardened and initialized with true raw data.")
