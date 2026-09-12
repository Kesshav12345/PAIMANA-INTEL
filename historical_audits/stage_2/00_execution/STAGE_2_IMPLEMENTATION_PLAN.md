# STAGE 2 IMPLEMENTATION PLAN

## 1. Goal Description
The objective of Stage 2 is to transform the heterogeneous PAIMANA source corpus (PDFs and Excel files) into a reproducible, provenance-preserving, validated, computation-ready, ML-ready analytical data system (SQLite database), strictly following the validated Stage 1 and Stage 1.5 specifications.

## 2. Dependency Order
The pipeline is strictly sequential to ensure immutability and provenance:
1. **Source Inventory & Manifest Generation** (Checkpoint 1)
2. **Extraction** (Checkpoint 2)
3. **Extraction Validation** (Checkpoint 3)
4. **Standardization** (Checkpoint 4)
5. **Identity Resolution** (Checkpoint 5)
6. **Canonical Load** (Checkpoint 6)
7. **Canonical Validation** (Checkpoint 7)
8. **Derived Computations** (Checkpoint 8)
9. **External Data Integration** (Checkpoint 9)
10. **ML Feature/Target Generation** (Checkpoint 10)
11. **Final Quality Audit** (Checkpoint 11)

## 3. Components, Inputs, Outputs, Scale
- **Components**: Python scripts, SQLite database (`paimana_analytical.db`), SQL schemas, Pytest test suites.
- **Inputs**: Primary dataset (~37 PDFs), Secondary dataset (~77 PDFs, mostly sector reports), External datasets (4 Excel files).
- **Outputs**: 
  - `01_raw/SOURCE_MANIFEST.csv`
  - Extracted JSONs/CSV
  - Canonical SQLite database with tables (`Dim_Project`, `Fact_Project_Observation`, `Fact_Sector_Performance`, `Dim_Report`, `Dim_Organization`, `Dim_Sector`, `Dim_State`).
- **Expected Scale**: ~120 PDF reports. ~50,000 - 80,000 project observations. ~500 sector performance observations.

## 4. Validation Strategy
- **Structural Tests**: Foreign keys, data types, nullability (via SQL constraints & testing).
- **Numerical/Temporal Tests**: Validating percentages <= 100% (where appropriate), date logical ordering (Original <= Revised <= Anticipated).
- **Reconciliation Tests**: Tracking record counts across stages (Raw -> Extracted -> Standardized -> Canonical).
- **Data Quality Tests**: Running an automated Pytest suite at each checkpoint.

## 5. Rollback Strategy
- **Idempotency**: All ETL scripts will be idempotent (clearing target tables/partitions before load or using upserts).
- **Version Control**: The source code (extraction scripts, SQL schema, computations) will be versioned. The SQLite database can be fully regenerated from raw sources in case of corruption.
- **Quarantine**: Ambiguous or failed records will not crash the pipeline or corrupt the database. They will be directed to quarantine tables/files for review.

## 6. Risks & Blockers
- **Risk**: Changes in PDF table layouts across the 15-month span may break regex or positional extraction rules.
- **Risk**: Difficulty in resolving Project Codes (QPISR) with PAIMANA IDs (Flash Reports) automatically without an explicit mapping document.
- **Blocker**: If a critical semantic mismatch (e.g., unit ambiguity) is found during extraction that contradicts the Stage 1.5 schema, implementation must halt until the schema is revised.

## 7. Required Human Decisions

### User Review Required
> [!WARNING]
> **Project Identity Resolution Strategy**
> Stage 1.5 found dual project identities: Flash Reports use numeric IDs (e.g., `702668`) while QPISR uses alphanumeric codes (e.g., `N18000296`). 
> **Question:** During Identity Resolution (Checkpoint 5), if we cannot algorithmically bridge these two identities via `Project Name`, should we treat them as distinct projects in `Dim_Project`, or quarantine them until a manual crosswalk is provided?

> [!NOTE]
> **Database Technology**
> The plan proposes using **SQLite** for the analytical data system. Given the expected scale (~100K rows), SQLite offers full relational integrity, perfect portability, and seamless integration with Python/Pandas for downstream ML extraction, fulfilling all requirements without the overhead of a dedicated RDBMS server. Do you approve of SQLite, or is PostgreSQL strictly required?

## 8. Checkpoints
1. `CHECKPOINT_1_MANIFEST`: Source manifest generated.
2. `CHECKPOINT_2_EXTRACTION`: PDFs extracted to structured text/JSON.
3. `CHECKPOINT_3_RAW_VALIDATION`: Extracted data validated against source expectations.
4. `CHECKPOINT_4_STANDARDIZATION`: Units, numbers, dates normalized.
5. `CHECKPOINT_5_IDENTITY`: Identities resolved.
6. `CHECKPOINT_6_CANONICAL`: `paimana_analytical.db` loaded.
7. `CHECKPOINT_7_CANONICAL_VALIDATION`: Constraints and relationships checked.
8. `CHECKPOINT_8_COMPUTATION`: Derived metrics computed.
9. `CHECKPOINT_9_EXTERNAL`: WPI/PPI integrated.
10. `CHECKPOINT_10_ML`: ML views generated.
11. `CHECKPOINT_11_AUDIT`: Final Data Quality and Adversarial Audit.
