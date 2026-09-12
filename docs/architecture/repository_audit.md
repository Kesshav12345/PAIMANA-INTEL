# Repository Audit

## 1. Current Tree Assessment
The repository has accumulated several phases of exploratory, analytical, and early implementation code. The root directory contains raw data folders (`Primary datasets`, `Secondary dataset`), loose documentation (`.docx`, `.txt`), and a mix of stage-specific folders alongside the new `src/`, `backend/`, and `data/` structure.

**Important Directories & Their Purpose:**
- `Primary datasets/` & `Secondary dataset/`: Original PDF and DOCX reports (Source Data). These should probably not live directly in Git if they become large, but act as the local raw ingestion point.
- `stage_1/` to `stage_2_5/`: Contain previous iterations of data extraction, validation, canonical DB loading, identity resolution, and comprehensive adversarial audits.
    - **Stage 2**: Contains the active Extraction pipeline (`01_raw`, `02_extraction`, `03_standardization`, `04_identity`). These are critical provenance generators.
    - **Stage 2.5**: Contains valuable audit scorecards and critical findings matrices.
- `src/` & `backend/` & `scripts/`: The beginnings of the Stage 3 transformation. Contains modular database, analytics, ML logic, and FastAPI scaffolds.
- `data/`: Contains the generated canonical SQLite database (`paimana_analytical.db`) and ML dataset.

## 2. Dependency Relationships & Dangerous Coupling
- **Data Lineage**: The new `src/` structure correctly depends on the `stage_2` outputs (identity-resolved JSONs), but the scripts are disjointed. The extraction pipeline lives in `stage_2` while the analytical consumption lives in `src/`.
- **Duplicated Responsibilities**: There are old ML scripts in `stage_2/09_ml` and old DB loaders in `stage_2/05_canonical` that are conceptually replaced by `src/ml` and `src/database`. This duplication is confusing.
- **Experimental vs Production**: `stage_1` and `stage_1_5` are purely historical documentation/audits. `stage_2` is a mix of production-intended extraction and deprecated analytics. `src/` is production-intended but incomplete.

## 3. Specific Risks Identified
- **ML Leakage Risks**: The previous `stage_2` ML script had target leakage (resolved in `src/ml`, but the old script still exists). The dataset generation needs rigorous point-in-time checks.
- **Analytics Risks**: Statistical formulas (e.g., Progress velocity, cost escalation) are currently embedded inside single scripts instead of a centralized formula registry.
- **Backend Risks**: The FastAPI scaffold in `backend/` currently queries the DB directly. It lacks service/repository layers and domain schemas.
- **Schema Problems**: The canonical DB `Fact_Project_Observation` correctly enforces (Project_SK, Report_SK), but lacks foreign keys to external references and detailed milestone tracking.

## 4. Proposed Target Structure
To satisfy the Master Prompt, the repository must be strictly separated by responsibility:

```text
paimana-intel/
├── docs/ (architecture, data, analytics, ml, api)
├── data/ (raw, standardized, resolved, canonical, ml)
├── src/paimana/ (the core package)
│   ├── ingestion/ (PDF/DOCX extraction)
│   ├── identity/ (Entity resolution)
│   ├── database/ (Repositories, Migrations)
│   ├── formulas/ (Deterministic registry)
│   ├── statistics/ (Trends, forecasting)
│   ├── ml/ (Features, Targets, Baseline models)
│   └── api/ (FastAPI routers, schemas, services)
├── scripts/ (CLI entrypoints: ingest, db-build, train, etc.)
├── tests/ (Unit, Integration, Leakage checks)
└── historical_audits/ (Archive of stage_1, stage_2.5 artifacts)
```
This structure ensures one source of truth, eliminates script duplication, and enforces the `SOURCE -> CANONICAL -> FORMULA -> ML -> API` pipeline.
