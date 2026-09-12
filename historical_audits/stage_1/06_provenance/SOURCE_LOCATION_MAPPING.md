# SOURCE LOCATION MAPPING

- **Source Table Identification**: In Stage 2 ETL, when extracting tables, generate a UUID for each extraction run and log:
  - File Path
  - File MD5 Hash
  - Report Year/Month
  - Page Number
  - Extracted JSON/CSV mapping
- This mapping forms the Dim_Source tracking layer.