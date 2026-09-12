# SCHEMA EVOLUTION

- The basic table structure appears relatively stable across recent reports, containing Project ID, Name, Cost metrics, and Physical Progress.
- **Known Risk**: Earlier reports (2015-2018) might not use the same 'Project ID' schema or might be entirely name-based. Stage 2 must perform fuzzy matching or historical mapping if Project IDs are missing in older datasets.