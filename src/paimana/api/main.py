from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from paimana.api.schemas import PortfolioSummary, SectorOverview, ProjectIntelligence
from paimana.api.repository import PaimanaRepository

app = FastAPI(
    title="PAIMANA INTEL API",
    description="Analytical API for Project Assessment and Infrastructure Monitoring",
    version="1.0.0"
)

repo = PaimanaRepository()

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "PAIMANA-INTEL"}

# ==========================================
# PORTFOLIO ANALYTICS
# ==========================================
@app.get("/portfolio/summary", response_model=PortfolioSummary)
def get_portfolio_summary():
    """Returns top-level KPIs: project count, total cost, expenditure."""
    return repo.get_portfolio_summary()

# ==========================================
# SECTOR ANALYTICS
# ==========================================
@app.get("/analytics/sectors", response_model=List[SectorOverview])
def get_sectors_overview():
    return repo.get_sector_overview()

# ==========================================
# PROJECT INTELLIGENCE
# ==========================================
@app.get("/projects/{project_sk}", response_model=ProjectIntelligence)
def get_project_intelligence(project_sk: int):
    """Returns the factors for a single project (where data is available)."""
    status = repo.get_project_status(project_sk)
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")
        
    history = repo.get_project_trajectory(project_sk)
    warnings = repo.get_project_warnings(project_sk)
    
    return ProjectIntelligence(
        current_status=status,
        trajectory=history,
        active_warnings=warnings
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
