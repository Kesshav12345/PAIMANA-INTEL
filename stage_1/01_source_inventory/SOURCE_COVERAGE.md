# SOURCE COVERAGE

- **Inspected Files**: A representative sample of Flash Reports and Complete Review Reports from 2025-2026.
- **Uncertainty**: The exact schema evolution from 2015 to 2025 is not fully mapped because we have only sampled the 2025/2026 schemas. Stage 2 ETL will need to dynamically map historical column names (e.g., if 'Cost' was named 'Sanctioned Cost' in 2015).
- **Extraction Method**: PDF tabular extraction via pdfplumber or PyMuPDF will yield rows of project records. OCR is not strictly required as the modern PDFs contain embedded text.