# KEYS AND IDENTITY

- **Natural Key**: Project_ID assigned by PAIMANA. Project_Name may be used as a fallback for older datasets where ID is absent.
- **Surrogate Keys**: To handle slowly changing dimensions (SCD Type 2), particularly if a project shifts agency or gets split.
- **Observation Identity**: The combination of Project_ID and Reporting_Month must be unique in the fact table.