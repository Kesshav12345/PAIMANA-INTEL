# DECISION LOG

- **Decision 1**: Adopt a Point-in-Time architecture for the ML dataset.
  - **Rationale**: Predicting cost overrun must replicate the exact state of knowledge available at month T. Using future revised costs would lead to severe target leakage.
- **Decision 2**: Exclude 'Status' from the ML training set if it represents the final completion status.
  - **Rationale**: Status is an outcome variable, not a feature.
- **Decision 3**: Extract PDF tabular data programmatically and deduplicate.
  - **Rationale**: The scale of 150+ PDFs requires a scalable ETL approach in Stage 2.