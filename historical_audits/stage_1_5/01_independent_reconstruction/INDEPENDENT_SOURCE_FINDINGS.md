# INDEPENDENT SOURCE FINDINGS

## Report Family Classification (Independently Verified)

### Family 1: Flash Reports (Project-Level Monitoring)
- **Count**: ~31 files (24 Primary + 3 older format + 4 archival duplicates)
- **Grain**: One row = One project at one reporting month
- **Columns**: S.NO., PROJECT ID, PROJECT NAME, ORIGINAL COST, REVISED COST, EXPENDITURE, PHYSICAL PROGRESS (%)
- **Page Structure**: Overview (page 3-4), NER section, HML Sector sections, Ministry sections, Appendix Tables (Table 1-6)
- **Table 6**: "All Ongoing Projects" — the complete project-level listing
- **Unique Identifier**: PROJECT ID (numeric, e.g., 702668)
- **Reporting Frequency**: Monthly
- **Time Reference**: "as of [Month Year]"
- **Verified From**: FlashReport_October_2025.pdf, FlashReport_April2026.pdf

### Family 2: Sector Performance Reviews (Sector-Level KPIs)
- **Count**: ~86 files (73 archival CRRs + 8 Primary CRRs + 5 Review Reports)
- **Grain**: One row = One infrastructure sector at one reporting month
- **Columns**: Sector, Unit, Achievement (current month), Achievement (previous year), Growth percent
- **Metrics**: Power (Billion Units), Coal (Million Tonnes), Steel (MT), Cement (MT), Fertilizers (MT), Crude Oil (MT), Natural Gas (MCM), Roads (Km), Railways (MT freight), Cargo (MT), Civil Aviation (passengers), Telecommunications
- **Page Structure**: Summary, Highlights, Areas of Concern, Sector-wise detailed analysis with charts
- **Time Reference**: Monthly performance + April-to-Month cumulative
- **Verified From**: CompleteReviewReportApril2015.pdf, CompleteReviewReportDec2020.pdf, CompleteReviewReportAugust2025.pdf, ReviewReportOct25.pdf

### Family 3: QPISR (Quarterly Project Implementation Status Report)
- **Count**: 1 file
- **Grain**: One row = One project at one reporting quarter
- **Tables**:
  - Table 1: Sector-wise Distribution (aggregate)
  - Table 2: State-wise Distribution (aggregate)
  - Table 3: Completed Projects (project-level)
  - Table 4: Added Projects (project-level)
  - Table 5: Frozen/Deleted Projects (project-level)
  - Table 6: North-East Region Projects (project-level)
  - Table 7: All Ongoing Projects (project-level, 1734 projects)
- **Columns (Table 7)**: State, Sector, Sl No, Project Name (Agency Name) (Project Code), Date of Approval (MM/YYYY), Date of Commissioning Original (Revised) {Anticipated} (MM/YYYY), Cost Original (Revised) {Anticipated} in Rs. Crore, Cumulative Expenditure in Rs. Crore, Physical Progress (%)
- **Unique Identifier**: Project Code (alphanumeric, e.g., N18000296)
- **Reporting Frequency**: Quarterly
- **Verified From**: QPISR_QR_1st_2025-26.pdf

## Key Semantic Facts Independently Established

1. The QPISR cost column contains THREE stacked values: Original, (Revised), {Anticipated}
2. The QPISR date column contains THREE stacked values: Original, (Revised), {Anticipated}
3. "N.A." is used for missing values in QPISR
4. Project Codes follow patterns like N18000296 (N + sector_code + sequence)
5. Some older Project Codes use format 180100210 (without N prefix)
6. QPISR Table 3 (Completed Projects) has DIFFERENT columns than Table 7 (Ongoing) — it lacks Date of Approval and has only Date of Commissioning Original
7. Flash Reports define Mega projects as >= 1000 crore and Major projects as < 1000 crore
8. The Flash Report threshold is Rs. 150 crore and above
9. Flash Reports exclude Ministry of Road Transport and Highways in some months ("may reflect from next month onwards")
10. QPISR Table 5 explicitly tracks Frozen/Deleted projects — a critical signal for survivorship bias
