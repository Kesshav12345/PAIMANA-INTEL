# Product Semantic Contract

## 1. Product Goals
PAIMANA-INTEL is an AI-powered Infrastructure Decision Support system. It transitions PAIMANA from a historical reporting repository into a predictive and analytical platform that answers:
- What exists? (Portfolio KPIs)
- Where is it? (Geography & Risk Density)
- What changed? (Recent Portfolio Changes)
- Why is it happening? (Drivers & Explanations)
- What should be done? (Interventions & Effectiveness)

## 2. Analytical Hierarchy
The product requires multi-level dimensional drill-downs:
- **Sector Analytics**: Sector Overview → Sector vs. State → Sector+State Projects → Project Intelligence
- **Ministry Analytics**: Ministry Overview → Ministry vs. Agency → Ministry+Agency Projects → Project Intelligence
- **State Analytics**: State Overview → State vs. Sector → State+Sector Projects → Project Intelligence

*All paths culminate in **Project Intelligence**, which is the core entity.*

## 3. Project Intelligence (The 15 Factors)
The lifecycle of a single project is analyzed across 15 semantic factors:
1. **Current Project Status** (Deterministic facts)
2. **Project Health Summary** (Executive assessment)
3. **Cost Forecast** (ML predicted overrun)
4. **Schedule Forecast** (ML predicted delay)
5. **Overall Implementation Risk** (Aggregated weighted score)
6. **Risk & Performance Trajectory** (Time-series trend)
7. **Active Warnings & Early-Warning Triggers** (Rule-based policy alerts)
8. **Why Is the Project Being Flagged?** (SHAP / feature attribution)
9. **Key Risk Drivers** (Statistical correlation)
10. **Warning & Risk History** (Chronological warning log)
11. **Benchmark Against Similar Projects** (Peer cohort comparison)
12. **Areas Requiring Official Attention** (Human-review prioritization)
13. **Recommended Interventions** (Rule-based actions)
14. **Intervention Tracking & Progress** (Workflow state machine)
15. **Intervention Outcome & Effectiveness** (Before/after evaluation)

## 4. Computational Boundaries
Strict separation between deterministic calculations and ML predictions is enforced:

### Deterministic / Statistical (DO NOT use ML)
- Time Elapsed %
- Cost Escalation Amount & %
- Expenditure %
- Physical & Financial Progress
- Progress Velocity & Acceleration
- Schedule Slippage (historical)
- Milestone Delay Count
- Trajectories (Rolling averages, standard deviations, linear trend slopes)
- Anomaly Detection (Percentiles, robust z-scores)
- Warning Triggers (Policy rules)

### Machine Learning (USE ML)
- Probability of Future Cost Overrun (Classification)
- Predicted Final Cost (Regression)
- Probability of Future Schedule Delay (Classification)
- Predicted Delay Duration (Regression)

## 5. ML Target Definitions & Leakage Controls
- **Target Construction**: ML labels must be defined based on *future* observations relative to the prediction timestamp. For example, `Target_Delayed_6M` means "Does a report exist > prediction_date where Schedule_Delay_Months > threshold?".
- **Feature Separation**: Features must strictly use data available at or before the cutoff date. Target-derived variables (e.g., final cost, final delay) must not leak into features.
- **Missing Data**: Null is not zero. Missing expenditures or dates must be semantically handled (e.g., missing indicators or explicit exclusions), not blindly zero-filled.

## 6. Implementation Readiness Classification
Based on the current canonical data volume (72 projects, 650 real observations):
- **Currently Computable**: Progress, Expenditure, Current Status, Basic History.
- **Computable after Analytics Engine**: Velocities, Trends, Divergence, Schedule Slippage.
- **ML-Dependent**: Cost/Schedule Forecasts, Risk Drivers (Requires synthetic augmentation or large historical batch ingestion to overcome sparsity).
- **Requires Future Data (Data-Blocked)**: Interventions, Warning History Tracking. These are **SCHEMA-READY / DATA-NOT-YET-AVAILABLE** and must not be fabricated from historical reports.
