from pydantic import BaseModel
from typing import List, Optional

class PortfolioSummary(BaseModel):
    projects_monitored: int
    approved_cost: float
    revised_cost: float
    cumulative_expenditure: float

class SectorOverview(BaseModel):
    sector: str
    project_count: int
    total_investment: float

class ProjectStatus(BaseModel):
    project_sk: int
    project_name: str
    sector: Optional[str]
    ministry: Optional[str]
    state: Optional[str]
    original_cost: Optional[float]
    revised_cost: Optional[float]
    anticipated_cost: Optional[float]
    cumulative_expenditure: Optional[float]
    physical_progress_pct: Optional[float]

class ProjectIntelligence(BaseModel):
    current_status: ProjectStatus
    trajectory: List[dict]
    active_warnings: List[dict]
