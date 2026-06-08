-- Create star schema for warehouse

-- Dimension: Patients
CREATE TABLE dim_patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    age INT,
    age_group VARCHAR(20),
    gender VARCHAR(50),
    ethnicity VARCHAR(50),
    socioeconomic_status VARCHAR(20),
    insurance_type VARCHAR(50)
);

-- Dimension: Diagnoses
CREATE TABLE dim_diagnoses (
    diagnosis_id INT IDENTITY(1,1) PRIMARY KEY,
    diagnosis_name VARCHAR(200),
    icd_10_code VARCHAR(10),
    diagnosis_category VARCHAR(100)
);

-- Dimension: Treatments
CREATE TABLE dim_treatments (
    treatment_id INT IDENTITY(1,1) PRIMARY KEY,
    treatment_name VARCHAR(200),
    treatment_type VARCHAR(50)
);

-- Dimension: Facilities
CREATE TABLE dim_facilities (
    facility_id INT IDENTITY(1,1) PRIMARY KEY,
    facility_name VARCHAR(100),
    facility_type VARCHAR(50)
);

-- Dimension: Time
CREATE TABLE dim_time (
    date_id INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day_of_week VARCHAR(20)
);

-- Fact: Clinical Visits
CREATE TABLE fact_clinical_visits (
    visit_id INT PRIMARY KEY,
    patient_id VARCHAR(20),
    diagnosis_id INT,
    treatment_id INT,
    facility_id INT,
    date_id INT,
    
    -- Measures
    length_of_stay_days INT,
    total_cost DECIMAL(10,2),
    readmission_30_days BIT,
    patient_satisfaction_score INT,
    adverse_event BIT,
    outcome VARCHAR(20),
    
    FOREIGN KEY (patient_id) REFERENCES dim_patients(patient_id),
    FOREIGN KEY (diagnosis_id) REFERENCES dim_diagnoses(diagnosis_id),
    FOREIGN KEY (treatment_id) REFERENCES dim_treatments(treatment_id),
    FOREIGN KEY (facility_id) REFERENCES dim_facilities(facility_id),
    FOREIGN KEY (date_id) REFERENCES dim_time(date_id)
);

-- Indexes for performance
CREATE INDEX idx_visits_patient ON fact_clinical_visits(patient_id);
CREATE INDEX idx_visits_date ON fact_clinical_visits(date_id);
CREATE INDEX idx_visits_diagnosis ON fact_clinical_visits(diagnosis_id);
