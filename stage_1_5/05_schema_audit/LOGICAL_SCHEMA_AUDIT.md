# LOGICAL SCHEMA AUDIT

## OVERVIEW
The Stage 1 Logical Schema (`04_canonical_model/LOGICAL_SCHEMA.md`) and Field Mappings were derived exclusively from one report type (Flash Reports), resulting in a fundamentally incomplete schema that will silently discard critical project data present in the QPISR.

## KEY FINDINGS

### 1. Missing Semantic Concept: Anticipated Cost (P1)
- **Stage 1 Schema:** Defines only `Original_Cost` and `Revised_Cost`.
- **Actual Data:** The QPISR report uses a three-level cost hierarchy: `Cost Original (Revised) {Anticipated} in Rs. Crore`.
- **Impact:** Collapsing "Anticipated Cost" (currently estimated final cost) into "Revised Cost" (last officially sanctioned cost) creates systematic measurement error for cost-overrun calculations.

### 2. Missing Triple-Valued Dates (P1)
- **Stage 1 Schema:** Defines a single `Anticipated_Completion_Date`.
- **Actual Data:** The QPISR contains three dates: `Date of Commissioning: Original (Revised) {Anticipated}`.
- **Impact:** Without separating these dates, it is impossible to compute schedule slippage (Revised - Original) or schedule overruns (Anticipated - Revised).

### 3. Missing `Date_of_Approval` (P2)
- **Stage 1 Schema:** Omitted.
- **Actual Data:** Present as a distinct column in QPISR.
- **Impact:** Required for calculating project duration and expected progress baselines.

### 4. Missing Geographic Information (P2)
- **Stage 1 Schema:** Defines `Geo_SK` but mapping is unclear for Flash Reports. QPISR explicitly lists `State` as a primary column.
- **Impact:** Cannot perform state-wise aggregation as requested in the ML stack (Part AE).

### 5. Expenditure Semantics are Unverified (P2)
- **Stage 1 Mapping:** Assumed `EXPENDITURE` in Flash Reports means "Cumulative Expenditure."
- **Actual Data:** While QPISR explicitly labels the column `Cumulative Expenditure`, Flash Reports simply say `EXPENDITURE`. If any Flash Report reports period expenditure instead of cumulative, downstream velocity calculations will be entirely wrong.

### 6. No Fact Table for Sector Performance (P0)
- **Stage 1 Schema:** Defines a single `Fact_Observation` table.
- **Actual Data:** 86 reports in the corpus are Sector Performance Reports containing KPIs like "Power Generation (BU)", not project observations.
- **Impact:** Attempting to ingest Sector Performance Reports into `Fact_Observation` will fail or create semantically corrupt data. A separate `Fact_Sector_Performance` table is mandatory.

## VERDICT
The Stage 1 Logical Schema is **REJECTED**. A new logical schema must be designed that supports the union of fields from Flash Reports and QPISR, and establishes a separate fact table for Sector Performance metrics.
