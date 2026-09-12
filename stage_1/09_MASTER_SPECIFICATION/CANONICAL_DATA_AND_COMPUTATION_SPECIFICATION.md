# CANONICAL DATA AND COMPUTATION SPECIFICATION

## 1. Executive Summary
This document serves as the master contract for Stage 2 engineering. It outlines the structure, semantics, transformations, and computational requirements for parsing 150+ historical project monitoring reports into a machine-learning-ready database.

## 2. Canonical Data Model
- **Fact Table**: \Fact_Observation\. Stores monthly project snapshots. Unique key: (Project_ID, Report_Month).
- **Dimension Tables**: \Dim_Project\, \Dim_Organization\, \Dim_Sector\, \Dim_Source\.

## 3. Data Transformations
- Cost values must be stripped of '₹' and ',' and cast to Floats.
- Missing Revised Costs default to Original Costs for variance calculation, unless specified otherwise.
- Identical archival datasets across directories must be deduplicated based on file hashes/names before processing.

## 4. Computations
- 138 explicitly defined features span basic calculations (duration, cost overrun), statistical trajectories (rolling progress/expenditure), and ML outcomes (Cost/Schedule probabilities).
- ML models require Point-In-Time (PIT) correctness; no data from 	 > n can be used to predict an outcome at time 
.

## 5. Provenance
- Every parsed row must include a \Source_Reference_SK\ linking back to the exact PDF name, report date, and extraction page.