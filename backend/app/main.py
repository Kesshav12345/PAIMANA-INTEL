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
    return {"message": "Welcome to the PAIMANA INTEL API"}

@app.get("/projects", response_model=List[Dict[str, Any]])
def get_projects():
    """Retrieve the current status of all projects."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # We query the View created in Stage 3 for O(1) current status lookup
    cursor.execute("SELECT * FROM View_Current_Project_Status")
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

@app.get("/projects/{project_sk}/history", response_model=List[Dict[str, Any]])
def get_project_history(project_sk: int):
    """Retrieve the historical timeline of a specific project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM View_Project_Timeline WHERE Project_SK = ?", (project_sk,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Project not found or has no history")
    return [dict(ix) for ix in rows]

if __name__ == "__main__":
    import uvicorn
    # To run: uvicorn backend.app.main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
