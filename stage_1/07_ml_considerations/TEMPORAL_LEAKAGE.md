# TEMPORAL LEAKAGE

- **Risk**: Using a future Revised Cost to calculate Cost Escalation for an observation in the past.
- **Mitigation**: ML features must only be computed using data explicitly available *on or before* the Report_Month_SK. The canonical database must store Revised Cost as an observation variable, not just a static project attribute.