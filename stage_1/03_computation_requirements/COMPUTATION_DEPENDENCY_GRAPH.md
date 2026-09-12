# COMPUTATION DEPENDENCY GRAPH

## Example Dependencies
- **Feature**: Cost Escalation %
  - Depends on: Original Cost, Revised Cost
  - Source: PDF Table (Flash Report or Complete Review)

- **Feature**: Expenditure %
  - Depends on: Expenditure, Revised Cost
  - Source: PDF Table

- **Feature**: ML Cost Overrun Probability
  - Depends on: Historical Trajectory Features, Cost Escalation %, Physical Progress %, Schedule Delay, Sector
  - Source: Aggregated historical canonical table

- **Feature**: Project Risk Score
  - Depends on: Cost Risk, Schedule Risk, Progress Risk, Milestone Risk
  - Source: Intermediate derived features.