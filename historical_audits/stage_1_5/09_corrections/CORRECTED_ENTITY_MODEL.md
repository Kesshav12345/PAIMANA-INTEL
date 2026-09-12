# CORRECTED ENTITY MODEL

## 1. Project
- **Grain**: One row = One unique infrastructure project.
- **Attributes**: PAIMANA_ID (Numeric, from Flash Reports), Project_Code (Alphanumeric, from QPISR), Project_Name, Sector_SK, Org_SK, State_SK, Date_of_Approval.
- **Note**: Requires identity resolution logic to link PAIMANA_ID and Project_Code if both exist for the same project.

## 2. Project Observation (Fact)
- **Grain**: One row = One project at a specific reporting period (Month or Quarter).
- **Attributes**: Original_Cost, Revised_Cost, Anticipated_Cost, Cumulative_Expenditure, Physical_Progress_Pct, Original_Completion_Date, Revised_Completion_Date, Anticipated_Completion_Date.

## 3. Sector Performance Observation (Fact)
- **Grain**: One row = One infrastructure sector at a specific reporting month.
- **Attributes**: Metric_Name (e.g., "Power Generation", "Coal Production"), Metric_Unit, Achievement_Value, Target_Value, Previous_Year_Value, Growth_Pct_YoY, Cumulative_Growth_Pct.

## 4. Report Document (Dimension)
- **Grain**: One row = One source PDF file.
- **Attributes**: Report_Type (FLASH_REPORT, QPISR, SECTOR_PERFORMANCE_REVIEW), Report_Date, Report_Period_Start, Report_Period_End, Source_File_Name, Source_File_Hash.

## 5. Organization (Dimension)
- **Grain**: One row = One authority.
- **Attributes**: Ministry_Name, Department_Name, Agency_Name.

## 6. Sector (Dimension)
- **Grain**: One row = One unified sector.
- **Attributes**: HML_Sector_Name (from Flash Reports), Ministry_Sector_Name (from QPISR), Infra_Performance_Sector_Name (from CRRs).
- **Note**: Acts as a crosswalk to resolve the three distinct sector taxonomies present in the corpus.

## 7. State (Dimension)
- **Grain**: One row = One state/union territory.
- **Attributes**: State_Name.
