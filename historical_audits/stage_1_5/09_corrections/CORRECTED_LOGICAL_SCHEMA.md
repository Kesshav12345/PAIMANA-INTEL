# CORRECTED LOGICAL SCHEMA

This schema supersedes the Stage 1 Logical Schema and accounts for the multi-valued fields in QPISR and the existence of Sector Performance Reports.

## Table: Dim_Project
- `Project_SK` (Surrogate Key)
- `PAIMANA_ID` (Natural Key — Flash Report numeric ID, nullable)
- `Project_Code` (Natural Key — QPISR alphanumeric code, nullable)
- `Project_Name` (String)
- `Sector_SK` (Foreign Key)
- `Org_SK` (Foreign Key)
- `State_SK` (Foreign Key)
- `Date_of_Approval` (Date, from QPISR)

## Table: Fact_Project_Observation
- `Observation_SK` (Surrogate Key)
- `Project_SK` (Foreign Key)
- `Report_SK` (Foreign Key)
- `Original_Cost` (Float)
- `Revised_Cost` (Float, nullable)
- `Anticipated_Cost` (Float, nullable, from QPISR)
- `Cumulative_Expenditure` (Float)
- `Physical_Progress_Pct` (Float)
- `Original_Completion_Date` (Date, nullable)
- `Revised_Completion_Date` (Date, nullable)
- `Anticipated_Completion_Date` (Date, nullable)

## Table: Fact_Sector_Performance
- `Observation_SK` (Surrogate Key)
- `Sector_SK` (Foreign Key)
- `Report_SK` (Foreign Key)
- `Metric_Name` (String, e.g., "Power Generation", "Coal Production")
- `Metric_Unit` (String, e.g., "Billion Units", "Million Tonnes")
- `Achievement_Value` (Float)
- `Target_Value` (Float, nullable)
- `Previous_Year_Value` (Float, nullable)
- `Growth_Pct_YoY` (Float, nullable)
- `Cumulative_Growth_Pct` (Float, nullable)

## Table: Dim_Report
- `Report_SK` (Surrogate Key)
- `Report_Type` (Enum: FLASH_REPORT | QPISR | SECTOR_PERFORMANCE_REVIEW)
- `Report_Date` (Date)
- `Report_Period_Start` (Date)
- `Report_Period_End` (Date)
- `Source_File_Name` (String)
- `Source_File_Hash` (String)

## Table: Dim_Organization
- `Org_SK` (Surrogate Key)
- `Ministry_Name` (String)
- `Department_Name` (String, nullable)
- `Agency_Name` (String, nullable)

## Table: Dim_Sector
- `Sector_SK` (Surrogate Key)
- `HML_Sector_Name` (String, used in Flash Reports)
- `Ministry_Sector_Name` (String, used in QPISR)
- `Infra_Performance_Sector_Name` (String, used in CRRs)

## Table: Dim_State
- `State_SK` (Surrogate Key)
- `State_Name` (String)
