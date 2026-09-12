# SOURCE RELATIONSHIPS

- **Primary Datasets vs Secondary Datasets**: Primary represents the recent/current project status (2025-2026), whereas secondary contains the historical pipeline (2015-2026) necessary for training ML models for cost and schedule overrun.
- **WPI/PPI**: Serves as external macro-economic indicators to be joined with the project data (likely by sector and time period) to adjust for inflation and calculate real cost escalation.
- **Computation Stack vs Datasets**: The computation stack specifies 138+ computations (progress, cost, ML predictions) that must be mapped to the PDF tables (which contain fields like ORIGINAL COST, REVISED COST, EXPENDITURE, PHYSICAL PROGRESS).