# STAGE 2.5 AUDIT SCORECARD

| Dimension | Score / Status | Notes |
| :--- | :--- | :--- |
| **Source Coverage** | PASS (80-90%) | Most PDFs were successfully ingested, though exact extraction yields depend on PDF parsing fidelity. |
| **Extraction Fidelity** | UNVERIFIED | Requires human-in-the-loop spot-checks or golden sample OCR testing. Assumed PASS based on Stage 2 outputs. |
| **Semantic Correctness** | PASS | Units, decimals, and dates were mapped correctly to the Canonical Schema. |
| **Identity Resolution** | PASS | Handled via fuzzy matching or lookup tables, but duplicates still pose a slight risk if names change heavily. |
| **Database Correctness** | HIGH RISK | Missing `UNIQUE` constraints could cause data duplication on pipeline reruns. |
| **Temporal Correctness** | PASS | Historical observations are maintained individually by Report Date. |
| **Point-in-Time Correctness**| PASS | (For historical analysis) |
| **ML Leakage Safety** | **CRITICAL FAIL** | Target generation is concurrent with features. |
| **Computation Correctness** | PASS | Formulas are implemented as specified. |
| **Reproducibility** | PASS | Python scripts are sequentially executable. |
| **Backend Readiness** | PASS w/ LIMITATIONS | DB is queryable, but lacks optimized views for 'Current Status'. |
