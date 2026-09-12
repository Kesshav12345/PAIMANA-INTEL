# STAGE 3 GATES & REPAIRS

To unlock Stage 3 (Backend, Analytics, ML, and Production Development), the following repairs must be applied to the Stage 2 implementation:

## 1. ML Leakage Repair
- **Action**: Rewrite `stage_2/09_ml/generate_ml_dataset.py`.
- **Details**: Instead of predicting `Schedule_Delay_Months > 0` on the current observation row, shift the target by performing a self-join on `Fact_Project_Observation` where `t2.Report_Date = t1.Report_Date + X months`. The ML model must predict if the project *will* experience a delay in the future based on its *current* features.

## 2. Database Integrity Constraints
- **Action**: Update the SQLite DDL in `stage_2/05_canonical/load_sqlite.py`.
- **Details**: Add a `UNIQUE (Project_SK, Report_SK)` constraint to `Fact_Project_Observation` and `Fact_Project_Derived`. Add `ON CONFLICT REPLACE` or `ON CONFLICT IGNORE` to the insert statements to ensure pipeline idempotency and prevent record duplication on reruns.

## 3. API Serving Views
- **Action**: Create materialized views or dedicated tables for API performance.
- **Details**: Create a `View_Current_Project_Status` that pre-calculates the `MAX(Report_Date)` per project to allow O(1) lookups by the backend without scanning the entire history table.

## 4. Missing Data Imputation Strategy
- **Action**: Standardize missing data in ML datasets.
- **Details**: Currently, `NULL` or missing values in extraction are pushed directly to the CSV. Establish a strict imputation logic (e.g., median imputation, -1 flags, or dropping) before handing the CSV over to training pipelines.
