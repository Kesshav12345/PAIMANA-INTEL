# CORRECTED FIELD MAPPINGS

This document supersedes the Stage 1 Field Mappings. It provides distinct mappings for each report family to appropriately route data into either `Fact_Project_Observation` or `Fact_Sector_Performance`.

## 1. Flash Reports -> Fact_Project_Observation

| Source Field (PDF) | Target Entity.Field | Transformation |
|--------------------|---------------------|----------------|
| `S.NO.` | None | Ignored |
| `PROJECT ID` | `Dim_Project.PAIMANA_ID` | String Cast |
| `PROJECT NAME` | `Dim_Project.Project_Name` | Trim whitespace, uppercase |
| `ORIGINAL COST (₹ crores)` | `Fact_Project_Observation.Original_Cost` | Remove commas, cast to float |
| `REVISED COST (₹ crores)` | `Fact_Project_Observation.Revised_Cost` | Remove commas, cast to float |
| `EXPENDITURE (₹ crores)` | `Fact_Project_Observation.Cumulative_Expenditure` | Remove commas, cast to float. (Verify semantics: Assume cumulative unless stated otherwise). |
| `PHYSICAL PROGRESS (%)` | `Fact_Project_Observation.Physical_Progress_Pct` | Cast to float |

## 2. QPISR (Table 7) -> Fact_Project_Observation

| Source Field (PDF) | Target Entity.Field | Transformation |
|--------------------|---------------------|----------------|
| `State` | `Dim_State.State_Name` | Trim whitespace |
| `Sector` | `Dim_Sector.Ministry_Sector_Name` | Trim whitespace |
| `Sl No` | None | Ignored |
| `Project Name (Agency Name) (Project Code)` | `Dim_Project.Project_Name`, `Dim_Organization.Agency_Name`, `Dim_Project.Project_Code` | Regex split to extract name, agency, and code |
| `Date of Approval (MM/YYYY)` | `Dim_Project.Date_of_Approval` | Parse to Date (1st of month) |
| `Date of Commissioning Original (Revised) {Anticipated} (MM/YYYY)` | `Fact_Project_Observation.Original_Completion_Date`, `Revised_Completion_Date`, `Anticipated_Completion_Date` | Regex split to extract 3 dates. Parse to Date. |
| `Cost Original (Revised) {Anticipated} in Rs. Crore` | `Fact_Project_Observation.Original_Cost`, `Revised_Cost`, `Anticipated_Cost` | Regex split to extract 3 values. Remove commas (handle Indian numbering), cast to float. Handle "(N.A.)" as NULL. |
| `Cumulative Expenditure in Rs. Crore` | `Fact_Project_Observation.Cumulative_Expenditure` | Remove commas, cast to float |
| `Physical Progress (%)` | `Fact_Project_Observation.Physical_Progress_Pct` | Cast to float |

## 3. Sector Performance Reports -> Fact_Sector_Performance

*Note: Table formats vary slightly across years. This mapping applies to the standard Sector Highlights table.*

| Source Field (PDF) | Target Entity.Field | Transformation |
|--------------------|---------------------|----------------|
| `Sector` | `Fact_Sector_Performance.Metric_Name` & `Dim_Sector.Infra_Performance_Sector_Name` | e.g. "Power Generation", "Coal" |
| `Unit` | `Fact_Sector_Performance.Metric_Unit` | e.g. "Billion Unit", "Million tonne" |
| `Achievement [Current Month]` | `Fact_Sector_Performance.Achievement_Value` | Cast to float |
| `Achievement [Previous Year Month]` | `Fact_Sector_Performance.Previous_Year_Value` | Cast to float |
| `Growth percent` | `Fact_Sector_Performance.Growth_Pct_YoY` | Cast to float |
