# CRITICAL FINDINGS REGISTER
Generated during Stage 2.5 Adversarial Audit.

> [!CAUTION]
> The following critical findings must be resolved before proceeding to Stage 3.

## F-001: Target Leakage in ML Dataset
- **Location**: `stage_2/09_ml/generate_ml_dataset.py`
- **Severity**: CRITICAL
- **Evidence**: The column `Target_Is_Delayed` is computed directly from `Schedule_Delay_Months` in the *same observation row*.
- **Impact**: Any predictive model trained on this dataset will achieve 100% artificial accuracy because the feature set implicitly or explicitly contains the target information. The target must be shifted to a future horizon (e.g., delay at T+6 months) relative to the features at time T.

## F-002: Missing Unique Constraint on Canonical Facts
- **Location**: `stage_2/05_canonical/load_sqlite.py` (and Schema)
- **Severity**: HIGH
- **Evidence**: The `Fact_Project_Observation` table lacks an explicit `UNIQUE(Project_SK, Report_SK)` constraint. 
- **Impact**: Rerunning the canonical load pipeline without dropping the database first, or extracting multiple duplicate JSONs, will result in duplicated observations in the analytical database.

## F-003: Backend Query Performance
- **Location**: Analytical Database Schema
- **Severity**: MEDIUM
- **Evidence**: There is no materialized view or denormalized table for the "Current Status" of all active projects.
- **Impact**: A backend API serving a frontend dashboard will need to scan the entire historical fact table and group by the maximum report date to find the current state of a project, which is inefficient.
