import sqlite3
from typing import List, Dict, Optional
from paimana.config import CANONICAL_DB_PATH
from paimana.api.schemas import PortfolioSummary, SectorOverview, ProjectStatus

class PaimanaRepository:
    def __init__(self):
        self.db_path = CANONICAL_DB_PATH

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_portfolio_summary(self) -> PortfolioSummary:
        conn = self._get_conn()
        cursor = conn.cursor()
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
        
        # Handle case where tables are empty
        if row and row['projects_monitored'] > 0:
            return PortfolioSummary(
                projects_monitored=row['projects_monitored'],
                approved_cost=row['approved_cost'] or 0.0,
                revised_cost=row['revised_cost'] or 0.0,
                cumulative_expenditure=row['cumulative_expenditure'] or 0.0
            )
        return PortfolioSummary(projects_monitored=0, approved_cost=0.0, revised_cost=0.0, cumulative_expenditure=0.0)

    def get_sector_overview(self) -> List[SectorOverview]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Sector as sector, COUNT(Project_SK) as project_count, SUM(Anticipated_Cost) as total_investment 
            FROM View_Current_Project_Status 
            GROUP BY Sector
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            SectorOverview(
                sector=row['sector'] or "Unknown",
                project_count=row['project_count'],
                total_investment=row['total_investment'] or 0.0
            ) for row in rows
        ]

    def get_project_status(self, project_sk: int) -> Optional[ProjectStatus]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM View_Current_Project_Status WHERE Project_SK = ?", (project_sk,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return ProjectStatus(
            project_sk=row['Project_SK'],
            project_name=row['Original_Project_Name'],
            sector=row['Sector'],
            ministry=row['Ministry'],
            state=row['State'],
            original_cost=row['Original_Cost'],
            revised_cost=row['Revised_Cost'],
            anticipated_cost=row['Anticipated_Cost'],
            cumulative_expenditure=row['Cumulative_Expenditure'],
            physical_progress_pct=row['Physical_Progress_Pct']
        )
        
    def get_project_trajectory(self, project_sk: int) -> List[dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM View_Project_Timeline WHERE Project_SK = ?", (project_sk,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def get_project_warnings(self, project_sk: int) -> List[dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Fact_Project_Warning WHERE Project_SK = ?", (project_sk,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
