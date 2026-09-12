# LOGICAL SCHEMA

## Table: Dim_Project
- Project_SK (Surrogate Key)
- Project_ID (Natural Key)
- Project_Name
- Sector_SK
- Org_SK
- Geo_SK
- Approval_Date

## Table: Fact_Observation
- Observation_SK
- Project_SK
- Report_Month_SK
- Original_Cost
- Revised_Cost
- Expenditure
- Physical_Progress
- Anticipated_Completion_Date
- Status

## Table: Dim_Organization
- Org_SK
- Ministry_Name
- Agency_Name