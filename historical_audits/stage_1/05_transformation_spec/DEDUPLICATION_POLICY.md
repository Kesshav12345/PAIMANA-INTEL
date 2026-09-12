# DEDUPLICATION POLICY

- The system must ensure that one Project_ID has exactly one record per Reporting_Month.
- If identical datasets are present in both 'project monitoring archival' and 'performance monitoring archival' folders, they must be deduplicated at the file level before ingestion.
- **Rule**: Distinct (Project_ID, Report_Month_SK) is the unique composite key for fact observations.