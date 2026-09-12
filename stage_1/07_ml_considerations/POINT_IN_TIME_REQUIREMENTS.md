# POINT IN TIME REQUIREMENTS

- The ML dataset must support 'Point-in-Time' (PIT) correctness.
- Every training sample must represent 'What did the system know about project X as of Month T?'.
- We achieve this by joining the Dim_Project to Fact_Observation exactly on Month T, and computing rolling historical features exclusively using observations from Month T-1, T-2, etc.