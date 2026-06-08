-- Create schema for research operations data mart
CREATE SCHEMA research_operations;
GO

-- ==============================================================================
-- RESEARCH OPERATIONS DATA MART
-- Purpose: Optimized for clinical trial tracking and patient-level analytics
-- ==============================================================================

-- Fact: Patient Summary (aggregated from warehouse)
CREATE TABLE research_operations.fact_patient_summary (
    patient_id VARCHAR(20) PRIMARY KEY,
    
    -- Demographics
    age INT,
    age_group VARCHAR(20),
    gender VARCHAR(50),
    ethnicity VARCHAR(50),
    insurance_type VARCHAR(50),
    
    -- Clinical Metrics (aggregated)
    total_visits INT,
    first_visit_date DATE,
    last_visit_date DATE,
    days_since_last_visit INT,
    
    -- Outcome Metrics
    total_cost DECIMAL(12,2),
    average_satisfaction_score DECIMAL(3,1),
    
    -- Quality Metrics
    readmissions_30_day INT,
    adverse_events_count INT,
    
    -- Risk Assessment
    high_risk_patient BIT,
    chronic_condition_count INT,
    
    -- Last Updated
    last_updated DATETIME DEFAULT GETDATE()
);

-- Dimension: Care Teams
CREATE TABLE research_operations.dim_care_teams (
    team_id INT IDENTITY(1,1) PRIMARY KEY,
    team_name VARCHAR(100),
    specialty VARCHAR(100),
    facility_name VARCHAR(100)
);

-- Dimension: Intervention Programs
CREATE TABLE research_operations.dim_interventions (
    intervention_id INT IDENTITY(1,1) PRIMARY KEY,
    intervention_name VARCHAR(100),
    intervention_type VARCHAR(50), -- Preventive, Treatment, Follow-up
    target_population VARCHAR(100)
);

-- Fact: Patient Interventions
CREATE TABLE research_operations.fact_patient_interventions (
    intervention_event_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_id VARCHAR(20),
    intervention_id INT,
    intervention_date DATE,
    outcome VARCHAR(50), -- Completed, In Progress, Declined
    
    FOREIGN KEY (patient_id) REFERENCES research_operations.fact_patient_summary(patient_id),
    FOREIGN KEY (intervention_id) REFERENCES research_operations.dim_interventions(intervention_id)
);

-- Indexes for performance
CREATE INDEX idx_patient_summary_risk ON research_operations.fact_patient_summary(high_risk_patient);
CREATE INDEX idx_patient_summary_last_visit ON research_operations.fact_patient_summary(last_visit_date);
CREATE INDEX idx_interventions_patient ON research_operations.fact_patient_interventions(patient_id);
CREATE INDEX idx_interventions_date ON research_operations.fact_patient_interventions(intervention_date);
