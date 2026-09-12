# MISSING DATA POLICY

- **NULL Costs**: If a Revised Cost is empty, default to Original Cost (unless defined differently by PAIMANA methodology).
- **Missing Progress**: Leave as NULL. Do not impute using averages, as this introduces look-ahead bias and invalidates ML performance.
- **Not Reported vs Zero**: Distinguish a reported 0% progress from a missing value.