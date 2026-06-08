# DAX Measures Documentation

## Clinical Performance Metrics

### Total Patients
```dax
Total Patients = DISTINCTCOUNT(fact_clinical_visits[patient_id])
```
**Purpose:** Count unique patients who had at least one visit  
**Use Case:** Executive dashboard KPI, volume tracking  
**Expected Range:** 5,000 (all patients in demo data)

---

### Total Visits
```dax
Total Visits = COUNTROWS(fact_clinical_visits)
```
**Purpose:** Count total clinical encounters  
**Use Case:** Volume metric, denominator for rates  
**Expected Range:** 5,000 (one visit per patient in demo data)

---

### Total Cost
```dax
Total Cost = SUM(fact_clinical_visits[total_cost])
```
**Purpose:** Sum of all healthcare expenditures  
**Use Case:** Financial tracking, cost analysis  
**Format:** Currency ($)  
**Expected Range:** ~$40M (demo data)

---

### Avg Cost per Visit
```dax
Avg Cost per Visit = DIVIDE([Total Cost], [Total Visits], 0)
```
**Purpose:** Average cost per clinical encounter  
**Use Case:** Efficiency metric, cost benchmarking  
**Format:** Currency ($)  
**Expected Range:** ~$7,941 (demo data)  
**Note:** Third parameter (0) prevents divide-by-zero errors

---

### Readmission Rate
```dax
Readmission Rate = 
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_clinical_visits), 
        fact_clinical_visits[readmission_30_days] = TRUE
    ),
    COUNTROWS(fact_clinical_visits),
    0
)
```
**Purpose:** Percentage of patients readmitted within 30 days  
**Use Case:** Quality metric, CMS penalty avoidance  
**Format:** Percentage (%)  
**Expected Range:** 10-20% typical, 15% in demo data  
**Benchmark:** <15% is industry standard goal  
**Note:** Boolean field requires `= TRUE` comparison

---

### Avg Satisfaction
```dax
Avg Satisfaction = AVERAGE(fact_clinical_visits[patient_satisfaction_score])
```
**Purpose:** Average patient satisfaction rating (1-10 scale)  
**Use Case:** Patient experience tracking, quality metric  
**Format:** Decimal (0.00)  
**Expected Range:** 1-10, typically 6-8  
**Benchmark:** >7.5 considered good

---

### Adverse Event Rate
```dax
Adverse Event Rate = 
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_clinical_visits), 
        fact_clinical_visits[adverse_event] = TRUE
    ),
    COUNTROWS(fact_clinical_visits),
    0
)
```
**Purpose:** Percentage of encounters with adverse events  
**Use Case:** Safety metric, risk management  
**Format:** Percentage (%)  
**Expected Range:** 1-5% typical, 3% in demo data  
**Benchmark:** <3% is target  
**Clinical Definition:** Unexpected harm caused by medical care

---

### Avg Length of Stay
```dax
Avg Length of Stay = AVERAGE(fact_clinical_visits[length_of_stay_days])
```
**Purpose:** Average hospital stay duration  
**Use Case:** Efficiency metric, capacity planning  
**Format:** Decimal (days)  
**Expected Range:** 0-7 days typical, 1.04 in demo (mixed outpatient/inpatient)  
**Note:** 0 days = same-day/outpatient visit

---

## Operational Metrics

### High Risk Patients
```dax
High Risk Patients = 
CALCULATE(
    COUNTROWS(fact_patient_summary),
    fact_patient_summary[high_risk_patient] = 1
)
```
**Purpose:** Count of patients flagged as high-risk  
**Use Case:** Care management, resource allocation  
**Source:** Data mart (fact_patient_summary table)  
**Expected Range:** 865 in demo data (~17% of population)  
**Risk Criteria:** Readmissions > 0 OR adverse events > 0 OR visits > 5

---

### Patients with Readmissions
```dax
Patients with Readmissions = 
CALCULATE(
    DISTINCTCOUNT(fact_clinical_visits[patient_id]),
    fact_clinical_visits[readmission_30_days] = TRUE
)
```
**Purpose:** Count of unique patients who experienced readmission  
**Use Case:** Quality improvement targeting  
**Expected Range:** 740 in demo data  
**Note:** Different from total readmission count (some patients readmitted multiple times)

---

### Avg Visits per Patient
```dax
Avg Visits per Patient = 
DIVIDE([Total Visits], [Total Patients], 0)
```
**Purpose:** Average number of visits per patient  
**Use Case:** Utilization metric, high-utilizer identification  
**Format:** Decimal  
**Expected Range:** 1.0 in demo data (by design), 2-5 typical in real data  
**Note:** High values (>10) may indicate chronic conditions or poor care coordination

---

### Treatment Success Rate
```dax
Treatment Success Rate = 
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_clinical_visits),
        fact_clinical_visits[outcome] IN {"Recovered", "Improved"}
    ),
    COUNTROWS(fact_clinical_visits),
    0
)
```
**Purpose:** Percentage of treatments with positive outcomes  
**Use Case:** Quality metric, provider performance  
**Format:** Percentage (%) or Decimal  
**Expected Range:** 60-80% typical, 73% in demo data  
**Clinical Definition:** "Recovered" = complete resolution, "Improved" = partial improvement

---

## Data Mart Specific Measures

### Total Patients (Data Mart)
```dax
Total Patients (Data Mart) = COUNTROWS(fact_patient_summary)
```
**Purpose:** Count of patients in data mart  
**Use Case:** Data mart-specific calculations, validation  
**Expected Range:** Should match warehouse patient count (5,000)  
**Note:** Separate measure ensures correct context when using data mart tables

---

## Advanced Calculations (Production Examples)

### Risk-Adjusted Readmission Rate
```dax
Risk Adjusted Readmission Rate = 
VAR ActualReadmissions = [Patients with Readmissions]
VAR ExpectedReadmissions = 
    SUMX(
        fact_clinical_visits,
        SWITCH(
            TRUE(),
            fact_clinical_visits[age] > 65, 0.18,
            fact_clinical_visits[chronic_condition] = TRUE, 0.15,
            0.10
        )
    )
RETURN
DIVIDE(ActualReadmissions, ExpectedReadmissions, 1)
```
**Purpose:** Readmission rate adjusted for patient risk factors  
**Use Case:** Fair provider comparison, quality benchmarking  
**Format:** Ratio (1.0 = expected, >1.0 = worse than expected)  
**Note:** Placeholder example - production would use validated risk models

---

### YoY Growth
```dax
YoY Visit Growth = 
VAR CurrentYear = [Total Visits]
VAR PriorYear = 
    CALCULATE(
        [Total Visits],
        DATEADD(dim_time[full_date], -1, YEAR)
    )
RETURN
DIVIDE(CurrentYear - PriorYear, PriorYear, 0)
```
**Purpose:** Year-over-year percentage change in visits  
**Use Case:** Trend analysis, volume forecasting  
**Format:** Percentage (%)  
**Note:** Requires continuous date column in time dimension

---

## Measure Organization Best Practices

### Naming Conventions
- Use clear, business-friendly names
- Avoid abbreviations unless universally understood
- Include units in name when ambiguous (e.g., "Avg Length of Stay" vs "LOS")

### Formatting
- Apply appropriate formats (%, $, decimal places)
- Use consistent decimal precision (0 or 2 places typically)
- Format in Power BI model, not in measure definition

### Comments
- Add descriptions to measures (right-click → Properties → Description)
- Document calculation logic for complex measures
- Include benchmark values in description

### Measure Table
- Store all measures in dedicated `_Measures` table (naming convention: underscore prefix)
- Organize by category using Display Folders (Clinical, Financial, Operational)
- Keep measure table visible in report view

---

## Performance Optimization

### Calculation Context
- Use CALCULATE() to modify filter context
- Avoid nested CALCULATE() when possible
- Use variables (VAR) for repeated calculations

### DirectQuery Considerations
- Simple aggregations (SUM, COUNT, AVERAGE) perform well
- Complex measures (RANKX, TOPN) may be slow
- Use aggregations in Power BI for frequently used metrics

### Testing
- Validate measures against SQL queries
- Test edge cases (zero values, nulls, empty filters)
- Monitor query performance with Performance Analyzer

---

## Validation Queries

### SQL Validation Example
```sql
-- Validate Readmission Rate measure
SELECT 
    CAST(SUM(CASE WHEN readmission_30_days = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS readmission_rate
FROM fact_clinical_visits;
-- Should match DAX measure output
```

---

## References

- DAX functions: https://dax.guide
- Healthcare quality metrics: CMS Hospital Compare methodology