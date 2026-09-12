# CRITICAL RED FLAGS

## P0 — Stage 2 MUST NOT Proceed

### RF-001: Report-Family Misidentification
- **What**: Stage 1 treats "Complete Review Reports" and "Review Reports" as project-level monitoring data. They are actually infrastructure sector performance reports (Power, Coal, Steel metrics).
- **Evidence**: Direct PDF inspection of CRR Aug 2025, CRR Apr 2015, CRR Dec 2020, ReviewReport Oct 2025.
- **Impact**: ~73 PDFs misclassified. ETL would produce semantically corrupt records.
- **Fix**: Reclassify into three report families. Build separate Fact_Sector_Performance table.

### RF-002: Schema Built on Single Source Type
- **What**: Field mappings derived only from Flash Reports. QPISR has 9 columns including triple-valued cost/date fields, Date of Approval, Project Code, State, Sector.
- **Evidence**: QPISR_QR_1st_2025-26.pdf Table 7 headers.
- **Impact**: Critical fields silently dropped during ingestion.
- **Fix**: Redesign schema to accommodate all project-level sources.

## P1 — Major Architectural Correction Required

### RF-003: Historical Project Data Does Not Exist (as assumed)
- **What**: The 73 archival "CompleteReviewReport" files are sector performance reports. Project-level data spans only ~12-14 months.
- **Impact**: ML trajectory features requiring multi-year history are not computable from this corpus.
- **Fix**: Revise ML data availability assessment. Consider alternative data sources or cross-validation approaches.

### RF-004: Anticipated_Cost Not Modeled
- **What**: QPISR has three cost tiers: Original, (Revised), {Anticipated}. Schema has only two.
- **Impact**: Cost-overrun calculations systematically biased.
- **Fix**: Add Anticipated_Cost to schema.

### RF-005: Triple-Valued Dates Not Modeled
- **What**: QPISR dates have Original, (Revised), {Anticipated} values.
- **Impact**: Schedule slippage computations impossible.
- **Fix**: Add Original_Completion_Date, Revised_Completion_Date, Anticipated_Completion_Date.

### RF-006: Sector Taxonomy Collision
- **What**: Three incompatible sector taxonomies (HML, Ministry, Infrastructure sectors).
- **Impact**: Cross-report aggregations produce incorrect sector totals.
- **Fix**: Build explicit crosswalk table.

### RF-007: Dual Project Identity Systems
- **What**: Flash Reports use numeric IDs. QPISR uses alphanumeric Project Codes.
- **Impact**: Cannot join Flash and QPISR observations without mapping.
- **Fix**: Create bridge table or verify whether IDs correspond.

## P2 — Important Correction Required

### RF-008: Missing Date_of_Approval
### RF-009: Expenditure Semantics Unverified for Flash Reports
### RF-010: Computation Count Underestimated (159 vs 138)
### RF-011: Indian Number System Parsing Underspecified
### RF-012: Byte-Identical Archives Not Flagged
