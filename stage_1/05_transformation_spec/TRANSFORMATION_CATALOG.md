# TRANSFORMATION CATALOG

- **Text Extraction**: PyMuPDF + pdfplumber for table grid parsing.
- **Type Casting**: Strings to Floats (Cost/Expenditure/Progress).
- **Derived Calculation Pipeline**: Generate all metrics from 03_COMPUTATION_REQUIREMENTS recursively on the canonical representation.
- **External Joins**: Left join WPI/PPI monthly index to the Fact_Observation table on Report_Month_SK and Sector_SK.