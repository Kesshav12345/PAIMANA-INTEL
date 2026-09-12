# TEMPORAL VERSIONING

- **Point-in-Time Correctness**: A model predicting risk in Dec 2023 must only see observations up to Nov 2023. Thus, Fact_Observation includes an As_Of_Date or Reporting_Date.
- **Revisions**: The Revised_Cost can change. We must track its value at each observation month rather than overwriting historical rows with the final revised cost.