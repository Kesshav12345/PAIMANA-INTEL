from fastapi import FastAPI, HTTPException
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

app = FastAPI(
    title="PAIMANA INTEL API",
    description="Analytical API for Project Assessment and Infrastructure Monitoring",
    version="1.0.0"
)

WORKSPACE = Path(r"c:\Users\kessh\OneDrive\Documents\PAIMANA INTEL")
DB_PATH = WORKSPACE / "data" / "canonical" / "paimana_analytical.db"

def get_db_connection():
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Database not found. Run pipeline first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "PAIMANA-INTEL"}

# ==========================================
# PORTFOLIO ANALYTICS
# ==========================================
@app.get("/portfolio/summary")
def get_portfolio_summary():
    """Returns top-level KPIs: project count, total cost, expenditure."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Query View_Current_Project_Status for the latest state of all projects
    cursor.execute("""
        SELECT 
            COUNT(Project_SK) as projects_monitored,
            SUM(Original_Cost) as approved_cost,
            SUM(Anticipated_Cost) as revised_cost,
            SUM(Cumulative_Expenditure) as cumulative_expenditure
        FROM View_Current_Project_Status
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

# ==========================================
# SECTOR ANALYTICS
# ==========================================
@app.get("/analytics/sectors")
def get_sectors_overview():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Sector, COUNT(Project_SK) as project_count, SUM(Anticipated_Cost) as total_investment 
        FROM View_Current_Project_Status 
        GROUP BY Sector
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

# ==========================================
# PROJECT INTELLIGENCE
# ==========================================
@app.get("/projects/{project_sk}")
def get_project_intelligence(project_sk: int):
    """Returns the 15 factors for a single project (where data is available)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Current Project Status
    cursor.execute("SELECT * FROM View_Current_Project_Status WHERE Project_SK = ?", (project_sk,))
    status = cursor.fetchone()
    
    if not status:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 6. Risk & Performance Trajectory (History)
    cursor.execute("SELECT * FROM View_Project_Timeline WHERE Project_SK = ?", (project_sk,))
    history = cursor.fetchall()
    
    # Active Warnings (from Fact_Project_Warning - currently empty but schema-ready)
    cursor.execute("SELECT * FROM Fact_Project_Warning WHERE Project_SK = ?", (project_sk,))
    warnings = cursor.fetchall()
    
    conn.close()
    
    return {
        "current_status": dict(status),
        "trajectory": [dict(h) for h in history],
        "active_warnings": [dict(w) for w in warnings]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
