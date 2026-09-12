# ML CONSIDERATIONS AUDIT

## OVERVIEW
The Stage 1 ML Considerations document (`07_ml_considerations/ML_DATASET_DESIGN.md`) correctly identified principles of temporal leakage but made a fatal assumption about data availability that invalidates the proposed training methodology.

## KEY FINDINGS

### 1. The "Historical Data" Illusion (P0)
- **Stage 1 Assumption:** ML models can be trained on longitudinal project-level data spanning 2015-2026, extracted from historical "Complete Review Reports."
- **Actual Reality:** The historical Complete Review Reports (2015-2026) are **Sector Performance Reports**, not project monitoring reports. Project-level data only exists in Flash Reports and QPISR from April 2025 to July 2026 (approx. 15 months).
- **Impact:** Time-series models and trajectory features (e.g., historical trajectory, long-term volatility) requiring multi-year history *cannot* be trained on this corpus. The dataset size is drastically smaller than Stage 1 assumed.

### 2. Disconnect from Schema Reality (P1)
- **Stage 1 Assumption:** Models will predict `Revised_Cost` overruns based on current `Expenditure` and `Physical_Progress`.
- **Actual Reality:** As identified in the schema audit, QPISR contains `Anticipated_Cost` and `Anticipated_Completion_Date`.
- **Impact:** The Target candidates must be updated to predict deviations against the `Anticipated` fields, which represent the actual estimated end-state, rather than just the `Revised` fields, which may just be intermediate approved milestones.

### 3. Missing Survivorship Bias Check (P2)
- **Actual Reality:** QPISR explicitly includes a table for "Frozen/Deleted Projects" (Table 5). 
- **Impact:** If ML models only train on currently "Ongoing" projects (Table 7 in QPISR or Table 6 in Flash Reports), they will suffer from severe survivorship bias. Projects that failed or were cancelled will be excluded from the training set, artificially skewing the model's understanding of risk.

## VERDICT
The Stage 1 ML Considerations are **REJECTED**. The ML strategy must be drastically re-scoped to acknowledge the 15-month limit on project data, and models must be redesigned to accommodate the true multi-valued cost/schedule fields (Original/Revised/Anticipated).
