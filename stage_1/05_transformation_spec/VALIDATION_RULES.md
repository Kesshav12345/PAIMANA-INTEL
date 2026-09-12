# VALIDATION RULES

1. Expenditure cannot be negative.
2. Physical_Progress must be between 0 and 100.
3. Original_Cost cannot be missing or zero (all tracked projects are >= 150 crore).
4. Observation dates cannot overlap/repeat for the same project in the same reporting month.
5. Cross-field: Revised_Cost must be recorded; if omitted, validation should throw a warning.