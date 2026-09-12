# UNIT NORMALIZATION

- **Currency**: All financial values in PAIMANA tables are presented in '₹ crores'. During extraction, string characters like '₹' and ',' must be stripped, and the numerical value cast to a standard Float.
- **Percentages**: Physical Progress is represented out of 100 (e.g., '95' for 95%). Stored directly as Float.
- **Base Year**: Real cost index WPI/PPI base years must be aligned when calculating inflation-adjusted variables.