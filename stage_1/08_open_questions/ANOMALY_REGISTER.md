# ANOMALY REGISTER

- **Anomaly 1**: Duplicate files exist between performance monitoring archival data and project monitoring archival.
  - **Resolution**: Deduplicate at the ingest step.
- **Anomaly 2**: PDF table extraction may sometimes merge columns if cell borders are invisible.
  - **Resolution**: Use strict coordinate-based extraction or text-flow analysis in pdfplumber during Stage 2 ETL.