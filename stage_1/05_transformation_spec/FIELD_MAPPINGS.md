# FIELD MAPPINGS

| Source Field (PDF) | Target Field (Canonical) | Transformation |
|--------------------|--------------------------|----------------|
| S.NO. | Omitted | Ignored |
| PROJECT ID | Project_ID | String Cast |
| PROJECT NAME | Project_Name | Trim whitespace, uppercase |
| ORIGINAL COST (Γé╣ crores) | Original_Cost | Remove commas, cast to float |
| REVISED COST (Γé╣ crores) | Revised_Cost | Remove commas, cast to float |
| EXPENDITURE (Γé╣ crores) | Expenditure | Remove commas, cast to float |
| PHYSICAL PROGRESS (%) | Physical_Progress | Cast to float |