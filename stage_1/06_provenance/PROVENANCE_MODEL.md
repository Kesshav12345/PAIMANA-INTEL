# PROVENANCE MODEL

- **Objective**: Every canonical value must be traceable back to its origin report, page, and table.
- **Design**: The canonical Fact_Observation table must contain a Source_Reference_SK mapping back to a Dim_Source containing details about the PDF file name, report date, and extraction metadata.