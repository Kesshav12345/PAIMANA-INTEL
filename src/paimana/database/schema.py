import sqlite3
from pathlib import Path
import json

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"

# We point directly to the resolved JSONs that were safely moved to historical_audits
IDENTITY_JSON_DIR = WORKSPACE / "historical_audits" / "stage_2" / "04_identity" / "resolved_json"

SCHEMA_SQL = """
-- DIMENSIONS
CREATE TABLE IF NOT EXISTS Dim_Project (
    Project_SK INTEGER PRIMARY KEY,
    Original_Project_Name TEXT,
    Sector TEXT,
    Ministry TEXT,
    State TEXT
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
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True)
        
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema successfully hardened and initialized.")
