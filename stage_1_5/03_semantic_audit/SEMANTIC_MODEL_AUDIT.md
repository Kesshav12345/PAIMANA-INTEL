# SEMANTIC MODEL AUDIT

## OVERVIEW
The Stage 1 Semantic Model (`02_semantic_model/ENTITY_MODEL.md`) failed to accurately represent the core entities and granularities of the source corpus. 

## KEY FINDINGS

### 1. Missing Entity: Sector Performance Observation (P0)
Stage 1 entirely missed the existence of **Infrastructure Sector Performance Reports** (the historical "Complete Review Reports" and "Review Reports"). 
- **Stage 1 Grain:** Assumed all PDFs mapped to `Project x Reporting Month`.
- **Actual Grain:** The vast majority of historical PDFs (~86 files) map to `Sector x Month`. 
- **Impact:** Attempting to force sector-level metrics (e.g., Power generation in BU, Coal production in MT) into a project-level observation table will fundamentally corrupt the database.

### 2. Incomplete Grain Definition for Project Observations (P1)
Stage 1 defined the grain for Project Observation as `Project x Reporting Month`. 
- While true for Flash Reports, the **QPISR** provides data at a `Project x Quarter` grain.
- Furthermore, the QPISR contains multi-valued attributes for a single point in time (Original, Revised, and Anticipated Costs/Dates).
- **Impact:** The semantic model must distinguish between reporting periods (Monthly vs. Quarterly) and support the three-tiered cost/date hierarchy.

### 3. Conflation of Sector Taxonomies (P1)
Stage 1 assumed a single "Sector" entity. The corpus actually contains three distinct sector taxonomies:
1. **HML 2022 Sectors** (used in Flash Reports: e.g., Transport & Logistics > Roads & Highways)
2. **Ministry-based Sectors** (used in QPISR: e.g., ROAD TRANSPORT AND HIGHWAYS, CIVIL AVIATION)
3. **Infrastructure Sectors** (used in CRRs: e.g., Power, Coal, Cement, Steel)
- **Impact:** Cross-report aggregations will fail without a crosswalk entity mapping these taxonomies.

### 4. Missing Entity: Report Document (P2)
Because the reports themselves carry semantic weight (e.g., a Flash Report vs. a QPISR vs. a CRR), the `Report` must be modeled as a first-class entity. Stage 1 embedded the reporting period directly into the observation but lost the context of *which report* generated the observation.

## VERDICT
The Stage 1 Semantic Model is **REJECTED**. It must be replaced with a model that correctly identifies the three distinct report families and their respective grains.
