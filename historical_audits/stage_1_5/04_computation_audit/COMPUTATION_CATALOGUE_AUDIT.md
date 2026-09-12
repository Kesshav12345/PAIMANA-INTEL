# COMPUTATION CATALOGUE AUDIT

## OVERVIEW
The Stage 1 Computation Audit failed to account for missing input features and historically unavailable data. It also incorrectly documented the total number of computations specified in the source document.

## KEY FINDINGS

### 1. Computation Count Underestimated (P2)
- **Stage 1 Claim:** The ML stack has 138 explicitly defined computational modules/features (Parts A through AB).
- **Actual Document:** The document explicitly lists computations through `#159`, extending to Part AF. Stage 1 completely ignored Parts AC (Data Quality Calculations), AD (Data/Model Monitoring), AE (Geographic/Portfolio Special Cases), and AF (Home Dashboard Calculations).
- **Impact:** 21 critical computational modules for ML monitoring and dashboards were dropped from the specification.

### 2. Missing Input: "Date of Approval" (P1)
- **Stage 1 Mapping:** Did not map a "Date of Approval" field in the schema.
- **Computation Requirement:** Computations `#1` through `#5` (Project duration, Elapsed duration, Time elapsed %) explicitly rely on the Date of Approval to calculate basic project baselines.
- **Impact:** The entire "Basic Project Calculations" section of the ML stack cannot be computed under Stage 1's schema.

### 3. Missing Inputs: Triple-Valued Dates (P1)
- **Stage 1 Mapping:** Modeled only a single `Anticipated_Completion_Date`.
- **Computation Requirement:** Computation `#33` (Schedule slippage) requires `Revised_Completion` minus `Original_Completion`. 
- **Impact:** Basic schedule overrun metrics are impossible to compute without modeling all three dates found in the QPISR.

### 4. Historical Data Impossibility for Trajectory Features (P0)
- **Stage 1 Assumption:** Trajectory features (rolling statistics, moving averages, etc.) can be calculated using historical data from 2015-2026.
- **Actual Availability:** The historical corpus (2015-2026) consists of **Sector Performance Reports**, not project-level reports. Project-level data only spans ~15 months (April 2025 - July 2026).
- **Impact:** Any computation requiring long-term historical project data (e.g., `#47-55` trajectory features, `#65` moving averages) is impossible to calculate reliably. The ML models cannot be trained as originally envisioned due to this structural lack of historical project-level data.

## VERDICT
The Stage 1 Computation Catalogue is **REJECTED**. It must be updated to reflect the full 159 computations and modified to acknowledge the impossibility of calculating long-term trajectory features.
