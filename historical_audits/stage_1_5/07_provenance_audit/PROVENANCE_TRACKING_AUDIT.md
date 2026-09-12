# PROVENANCE TRACKING AUDIT

## OVERVIEW
The Stage 1 Provenance specification (`06_provenance/PROVENANCE_MODEL.md`) correctly specified the need to map observations back to source files and pages. However, because Stage 1 fundamentally misunderstood the source corpus, the provenance model is inadequate for tracing data across the disparate report families.

## KEY FINDINGS

### 1. Missing Report Type Dimension (P1)
- **Stage 1 Provenance:** Tracks `Source_File_Hash` and `Source_Page`.
- **Actual Reality:** A project observation extracted from a Flash Report is semantically different from one extracted from a QPISR (which represents a quarterly rollup and includes anticipated costs). 
- **Impact:** The provenance model must explicitly track `Report_Type` (e.g., `FLASH_REPORT`, `QPISR`, `SECTOR_PERFORMANCE_REVIEW`). If it does not, downstream models cannot weigh the reliability or semantic intent of conflicting observations.

### 2. Dual Project Identity Systems (P1)
- **Stage 1 Provenance:** Assumes a single, unified `Project_ID` exists natively.
- **Actual Reality:** Flash Reports use a numeric PAIMANA ID (e.g., `702668`). The QPISR uses an alphanumeric Project Code (e.g., `N18000296`). 
- **Impact:** The provenance pipeline must track the *original source identifier* alongside any resolved surrogate key. Without this, debugging failed identity resolutions (where a project in a Flash Report fails to join with its QPISR counterpart) will be impossible.

### 3. Sector Taxonomy Provenance (P2)
- **Stage 1 Provenance:** Does not track taxonomy origins.
- **Actual Reality:** The corpus uses three different sector taxonomies (HML, Ministry, Infrastructure). 
- **Impact:** When a project is assigned to a canonical sector, the provenance system must record *which* taxonomy the original sector string came from, to allow for auditing of the crosswalk logic.

## VERDICT
The Stage 1 Provenance Tracking is **INCOMPLETE**. It must be extended to include `Report_Type`, `Source_Project_Identifier`, and `Source_Taxonomy` to maintain data lineage across the heterogeneous corpus.
