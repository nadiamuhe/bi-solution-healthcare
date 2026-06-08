# Data Dictionary

## Warehouse Tables (dbo schema)

### fact_clinical_visits
**Description:** Core fact table containing all patient clinical encounters

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| visit_id | INT | Unique visit identifier | 1 |
| patient_id | VARCHAR(20) | Foreign key to dim_patients | P100000 |
| diagnosis_id | INT | Foreign key to dim_diagnoses | 12 |
| treatment_id | INT | Foreign key to dim_treatments | 5 |
| facility_id | INT | Foreign key to dim_facilities | 1 |
| date_id | INT | Foreign key to dim_time | 20220115 |
| length_of_stay_days | INT | Hospital stay duration | 3 |
| total_cost | DECIMAL(10,2) | Total encounter cost in USD | 7500.50 |
| readmission_30_days | BIT | Readmitted within 30 days | 1 (TRUE) |
| patient_satisfaction_score | INT | Score from 1-10 | 8 |
| adverse_event | BIT | Adverse event occurred | 0 (FALSE) |
| outcome | VARCHAR(20) | Treatment outcome | Recovered, Improved, Unchanged, Worsened |

**Grain:** One row per clinical visit  
**Row Count:** 5,000

---

### dim_patients
**Description:** Patient demographic information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| patient_id | VARCHAR(20) | Unique patient identifier (PK) | P100000 |
| age | INT | Patient age at visit | 45 |
| age_group | VARCHAR(20) | Age category | 36-50 |
| gender | VARCHAR(50) | Patient gender | Female, Male, Non-binary |
| ethnicity | VARCHAR(50) | Patient ethnicity | White, Black, Hispanic, Asian, Indigenous, Other |
| socioeconomic_status | VARCHAR(20) | SES category | Low, Medium, High |
| insurance_type | VARCHAR(50) | Insurance coverage | Private Insurance, Medicare, Medicaid, Uninsured |

**Grain:** One row per unique patient  
**Row Count:** 5,000

---

### dim_diagnoses
**Description:** Medical diagnosis information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| diagnosis_id | INT | Unique diagnosis identifier (PK, Identity) | 1 |
| diagnosis_name | VARCHAR(200) | Full diagnosis name | Type 2 Diabetes |
| icd_10_code | VARCHAR(10) | ICD-10 code | E11 |
| diagnosis_category | VARCHAR(100) | Clinical category | Metabolic, Cardiovascular, Respiratory, etc. |

**Grain:** One row per unique diagnosis  
**Row Count:** 18

---

### dim_treatments
**Description:** Treatment and intervention information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| treatment_id | INT | Unique treatment identifier (PK, Identity) | 1 |
| treatment_name | VARCHAR(200) | Full treatment name | Metformin |
| treatment_type | VARCHAR(50) | Treatment category | Medication, Surgery, Therapy, Procedure, Lifestyle |

**Grain:** One row per unique treatment  
**Row Count:** 40+

---

### dim_facilities
**Description:** Healthcare facility information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| facility_id | INT | Unique facility identifier (PK, Identity) | 1 |
| facility_name | VARCHAR(100) | Facility name | University Medical Center |
| facility_type | VARCHAR(50) | Facility category | Hospital, Clinic |

**Grain:** One row per facility  
**Row Count:** 5

---

### dim_time
**Description:** Date dimension for temporal analysis

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date_id | INT | Date identifier (PK, YYYYMMDD format) | 20220115 |
| full_date | DATE | Full date value | 2022-01-15 |
| year | INT | Calendar year | 2022 |
| quarter | INT | Calendar quarter | 1 |
| month | INT | Month number | 1 |
| month_name | VARCHAR(20) | Month name | January |
| day_of_week | VARCHAR(20) | Day name | Saturday |

**Grain:** One row per date  
**Row Count:** ~1,095 (3 years)

---

## Data Mart Tables (research_operations schema)

### fact_patient_summary
**Description:** Patient-level aggregated metrics for research operations

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| patient_id | VARCHAR(20) | Unique patient identifier (PK) | P100000 |
| age | INT | Patient age | 58 |
| age_group | VARCHAR(20) | Age category | 51-65 |
| gender | VARCHAR(50) | Patient gender | Female |
| ethnicity | VARCHAR(50) | Patient ethnicity | White |
| insurance_type | VARCHAR(50) | Insurance coverage | Private Insurance |
| total_visits | INT | Lifetime visit count | 1 |
| first_visit_date | DATE | Date of first encounter | 2022-01-15 |
| last_visit_date | DATE | Date of most recent encounter | 2022-01-15 |
| days_since_last_visit | INT | Days since last contact | 1506 |
| total_cost | DECIMAL(12,2) | Cumulative healthcare costs | 7500.50 |
| average_satisfaction_score | DECIMAL(3,1) | Average satisfaction (1-10) | 8.5 |
| readmissions_30_day | INT | Count of 30-day readmissions | 0 |
| adverse_events_count | INT | Count of adverse events | 0 |
| high_risk_patient | BIT | High-risk flag | 1 (TRUE) |
| chronic_condition_count | INT | Number of chronic conditions | 2 |
| last_updated | DATETIME | Last ETL refresh timestamp | 2026-02-23 10:30:00 |

**Grain:** One row per patient (aggregated from visits)  
**Row Count:** 5,000

**Business Rules:**
- `high_risk_patient = 1` when: readmissions > 0 OR adverse_events > 0 OR total_visits > 5
- `chronic_condition_count` based on visit frequency and readmission patterns

---

### dim_interventions
**Description:** Patient intervention programs

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| intervention_id | INT | Unique intervention identifier (PK, Identity) | 1 |
| intervention_name | VARCHAR(100) | Program name | Diabetes Management Program |
| intervention_type | VARCHAR(50) | Intervention category | Preventive, Treatment, Follow-up |
| target_population | VARCHAR(100) | Intended patient group | Type 2 Diabetes patients |

**Grain:** One row per intervention program  
**Row Count:** 5

---

### dim_care_teams
**Description:** Clinical care team information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| team_id | INT | Unique team identifier (PK, Identity) | 1 |
| team_name | VARCHAR(100) | Care team name | Primary Care Team A |
| specialty | VARCHAR(100) | Clinical specialty | Primary Care |
| facility_name | VARCHAR(100) | Associated facility | University Medical Center |

**Grain:** One row per care team  
**Row Count:** 5

---

### fact_patient_interventions
**Description:** Patient intervention tracking (currently unpopulated)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| intervention_event_id | INT | Unique event identifier (PK, Identity) | 1 |
| patient_id | VARCHAR(20) | Foreign key to fact_patient_summary | P100000 |
| intervention_id | INT | Foreign key to dim_interventions | 1 |
| intervention_date | DATE | Date intervention occurred | 2023-05-15 |
| outcome | VARCHAR(50) | Intervention result | Completed, In Progress, Declined |

**Grain:** One row per intervention event  
**Row Count:** 0 (table structure only)

---

## Data Quality Rules

### Referential Integrity
- All foreign keys in fact tables must exist in corresponding dimension tables
- No orphaned records allowed

### Data Validation
- `patient_satisfaction_score`: Range 1-10
- `length_of_stay_days`: Non-negative integer
- `total_cost`: Positive decimal
- `age`: Range 1-100
- `readmission_30_days`, `adverse_event`, `high_risk_patient`: Boolean (0 or 1)

### Business Logic
- `outcome` values: Recovered, Improved, Unchanged, Worsened only
- `date_id` format: YYYYMMDD (e.g., 20220115)
- Treatment must be clinically appropriate for diagnosis

---

## Notes

**Synthetic Data:** All patient identifiers, names, and clinical details are synthetically generated for demonstration purposes. No real patient information is included.

**HIPAA Compliance:** Data follows Safe Harbor de-identification methodology with all 18 HIPAA identifiers removed or generalized.