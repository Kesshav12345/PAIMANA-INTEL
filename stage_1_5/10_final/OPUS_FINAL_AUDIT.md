# STAGE 1.5 — ADVERSARIAL AUDIT

## EXECUTIVE VERDICT

**STAGE 2 STATUS: NOT READY**
Stage 1 contains a P0-critical foundational error that would corrupt the entire downstream data system if Stage 2 proceeded on its basis.

---

## TOP 12 FINDINGS (RANKED BY SEVERITY)

### FINDING 1 — P0-CRITICAL: FUNDAMENTAL REPORT-FAMILY MISIDENTIFICATION

Stage 1 treats all PDFs as homogeneous project-monitoring reports. This is factually wrong.

Independent source inspection reveals the corpus contains three fundamentally different report families that Stage 1 collapsed into one:

| Report Family | Actual Content | Grain | Stage 1 Treatment |
|---|---|---|---|
| Flash Reports (FlashReport, FR) | PAIMANA project-level monitoring data | Project x Reporting Month | Correctly sampled |
| Complete Review Reports / Review Reports | Infrastructure Sector Performance (Power in BU, Coal in MT, Steel production, etc.) | Sector x Month | MISIDENTIFIED AS PROJECT DATA |
| QPISR | Quarterly project-level monitoring data | Project x Quarter | Mentioned but not semantically analyzed |

Source evidence:
- CompleteReviewReportAugust2025.pdf Page 2: Contents listing "1. Power, 2. Coal, 3. Steel, 4. Cement, 5. Fertilizers..."
- CompleteReviewReportApril2015.pdf Page 1: "REVIEW OF INFRASTRUCTURE SECTOR PERFORMANCE (April 2015)"
- ReviewReportOct25.pdf Page 2: Contents listing "1. Power, 2. Coal, 3. Steel..."
- FlashReport_April2026 (2).pdf Page 4: "1981 Ongoing Projects | 17 Line Ministries" with Project IDs, costs, progress.
- QPISR_QR_1st_2025-26.pdf Page 2: "Table:-7. Project List: Ongoing Projects" with 9 columns.

Downstream consequence: If Stage 2 parses ~73 CRR PDFs as project-level records, it will produce semantically corrupt records.

Severity: P0

---

### FINDING 2 — P0-CRITICAL: SCHEMA BUILT ON WRONG SOURCE

Stage 1 FIELD_MAPPINGS.md maps only: S.NO. | PROJECT ID | PROJECT NAME | ORIGINAL COST | REVISED COST | EXPENDITURE | PHYSICAL PROGRESS (%)

This mapping is valid only for Flash Reports (~30 files). The QPISR has 9 columns including Date of Approval, triple-valued dates, triple-valued costs, State, Sector, Agency, Project Code.

Severity: P0

---

### FINDING 3 — P1: "ANTICIPATED COST" IS A SEPARATE SEMANTIC CONCEPT

QPISR uses Cost Original (Revised) {Anticipated} in Rs. Crore.
Example: CIVIL AVIATION: 28,200.17 (29,521.45) {32,130.66}

Stage 1 schema has only Original_Cost and Revised_Cost. No Anticipated_Cost.

Severity: P1

---

### FINDING 4 — P1: DATE FIELDS ARE TRIPLE-VALUED, NOT SINGLE

QPISR: Date of Commissioning: Original (Revised) {Anticipated} (MM/YYYY)
Example: 6/2024 (01-03-2026) {3/2026}

Stage 1 schema has a single Anticipated_Completion_Date. Missing Original and Revised completion dates.

Severity: P1

---

### FINDING 5 — P1: HISTORICAL CRRs ARE NOT PROJECT DATA

All CRRs from 2015-2026 are sector-performance reports. The longitudinal project data 2015-2026 that Stage 1 assumed does NOT exist in this corpus.

Actual project-level data spans only ~12-14 months (Jul 2025 - Jul 2026).

Severity: P1

---

### FINDING 6 — P1: DUPLICATE ARCHIVES ARE BYTE-IDENTICAL

Both archival directories (77 files each) are byte-for-byte identical. Stage 1 understated this as "overlapping."

Severity: P1

---

### FINDING 7 — P1: SECTOR CLASSIFICATION MISMATCH

Three different sector taxonomies exist:
- Flash Reports: HML 2022 (Transport and Logistics > Roads and Highways, Railways, etc.)
- QPISR: Ministry-based (CIVIL AVIATION, COAL, PETROLEUM, etc.)
- CRRs: Infrastructure sectors (Power, Coal, Steel, Cement, Fertilizers, etc.)

Stage 1 assumes a single taxonomy.

Severity: P1

---

### FINDING 8 — P2: MISSING DATE OF APPROVAL

QPISR contains Date of Approval (MM/YYYY). Not in Stage 1 schema. Required for project duration calculations.

Severity: P2

---

### FINDING 9 — P2: DUAL PROJECT IDENTITY SYSTEMS

Flash Reports use numeric PROJECT ID (e.g., 702668).
QPISR uses alphanumeric Project Code (e.g., N18000296).
Stage 1 does not distinguish these.

Severity: P2

---

### FINDING 10 — P2: EXPENDITURE SEMANTICS VARY

QPISR explicitly labels "Cumulative Expenditure." Flash Reports label just "EXPENDITURE." Stage 1 assumes cumulative without evidence for Flash Reports.

Severity: P2

---

### FINDING 11 — P2: COMPUTATION COUNT IS 159, NOT 138

The ML stack document enumerates through computation #159 (Parts AC-AF). Stage 1 claims 138.

Severity: P2

---

### FINDING 12 — P2: INDIAN NUMBER SYSTEM

QPISR uses mixed formatting including Indian commas (2,01,738.62). Stage 1 transformation spec underspecifies this.

Severity: P2

---

## CLAIM-EVIDENCE AUDIT

| Stage 1 Claim | Evidence | Verdict |
|---|---|---|
| CRRs are project monitoring data | CRR content is Power/Coal/Steel metrics | FALSE |
| Review Reports are project monitoring data | Content is Power/Coal/Steel metrics | FALSE |
| Historical data spans 2015-2026 for projects | Only Flash Reports (2025-2026) and QPISR (1 file) contain project data | FALSE |
| Project_ID is the natural key | Two ID systems exist | UNVERIFIED |
| Schema has Original_Cost and Revised_Cost | QPISR has THREE cost values | INCOMPLETE |
| Expenditure is cumulative | Stated only in QPISR header | UNVERIFIED for Flash Reports |
| 138 computations in ML stack | Document contains at least 159 | INCORRECT |
| Two archival folders overlap | They are byte-identical copies | UNDERSTATED |

---

## CORRECTED SOURCE INVENTORY

### Project-Level Data Sources
| Source | Files | Date Range | IDs | Dates | Progress |
|---|---|---|---|---|---|
| Flash Reports (Primary) | ~24 | Jul 2025 - Apr 2026 | Numeric | No | Yes |
| Flash Reports (Archival) | 4 | Apr - Jul 2026 | Numeric | No | Yes |
| QPISR | 1 | Q1 2025-26 | Alphanumeric code | Triple-valued | Yes |
| FR older format | 3 | Apr-Jun 2025 | Numeric | No | Yes |

### Sector-Performance Data Sources
| Source | Files | Date Range | Content |
|---|---|---|---|
| CRRs (Primary) | 8 | Dec 2020 - Aug 2025 | Sector KPIs |
| Review Reports (Primary) | 5 | Sep 2025 - Jan 2026 | Sector KPIs |
| CRRs (Archival) | 73 | Apr 2015 - Jul 2026 | Sector KPIs |

---

## CORRECTED LOGICAL SCHEMA

Table: Dim_Project
  - Project_SK (Surrogate Key)
  - PAIMANA_ID (Flash Report numeric ID, nullable)
  - Project_Code (QPISR alphanumeric code, nullable)
  - Project_Name
  - Sector_SK
  - Org_SK
  - State_SK
  - Date_of_Approval

Table: Fact_Project_Observation
  - Observation_SK
  - Project_SK
  - Report_SK
  - Report_Period_SK
  - Original_Cost
  - Revised_Cost (nullable)
  - Anticipated_Cost (nullable)
  - Cumulative_Expenditure
  - Physical_Progress_Pct
  - Original_Completion_Date (nullable)
  - Revised_Completion_Date (nullable)
  - Anticipated_Completion_Date (nullable)
  - Source_Page
  - Source_Table

Table: Fact_Sector_Performance
  - Observation_SK
  - Sector_SK
  - Report_SK
  - Report_Period_SK
  - Metric_Name
  - Metric_Unit
  - Achievement_Value
  - Target_Value (nullable)
  - Previous_Year_Value (nullable)
  - Growth_Pct_YoY (nullable)
  - Cumulative_Growth_Pct (nullable)

Table: Dim_Report
  - Report_SK
  - Report_Type (FLASH_REPORT | QPISR | SECTOR_PERFORMANCE_REVIEW)
  - Report_Date
  - Report_Period_Start
  - Report_Period_End
  - Source_File_Name
  - Source_File_Hash

Table: Dim_Organization
  - Org_SK
  - Ministry_Name
  - Department_Name (nullable)
  - Agency_Name (nullable)

Table: Dim_Sector
  - Sector_SK
  - HML_Sector_Name
  - Ministry_Sector_Name
  - Infra_Performance_Sector_Name

---

## STAGE 2 GATES

| Gate | Condition | Status |
|---|---|---|
| GATE 1 | Report families correctly classified | FAIL |
| GATE 2 | Grain validated per report type | FAIL |
| GATE 3 | Entity model includes sector performance | FAIL |
| GATE 4 | Schema includes triple-valued cost/date fields | FAIL |
| GATE 5 | Project identity resolution plan for dual ID systems | FAIL |
| GATE 6 | Sector taxonomy crosswalk defined | FAIL |
| GATE 7 | Historical data availability honestly assessed | FAIL |
| GATE 8 | Units validated per source | PARTIAL |
| GATE 9 | Provenance model includes report type | PARTIAL |
| GATE 10 | ML leakage analysis updated for actual data availability | FAIL |

---

## MANDATORY FIXES BEFORE STAGE 2

1. Reclassify source corpus into three report families
2. Redesign schema to include Fact_Sector_Performance
3. Add Anticipated_Cost field
4. Add triple-valued date fields
5. Add Date_of_Approval
6. Resolve dual project identity systems
7. Create sector taxonomy crosswalk
8. Honestly assess ML training data availability (~12-14 months, not 11 years)
9. Separate Dim_Report as first-class entity
10. Update computation availability matrix

## DO NOT IMPLEMENT YET

1. Any ML model training until longitudinal project data availability is confirmed
2. Velocity/acceleration computations until sufficient monthly data exists
3. Historical schema evolution mapping until actual project-data sources are fully parsed
