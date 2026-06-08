"""
ETL: Populate Research Operations Data Mart from Warehouse
Aggregates visit-level data to patient-level summaries
"""

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import os
import urllib.parse
from sqlalchemy import create_engine, text

# Azure SQL connection
server = 'YOUR-SERVER-NAME.database.windows.net'
database = 'HealthcareAnalytics'
username = 'YOUR-SQL-USERNAME'
password = 'YOUR-SQL-PASSWORD'


odbc_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{server},1433;"
    f"Database={database};"
    f"Uid={username};"
    f"Pwd={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=120;"
)

connect_str = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)

engine = create_engine(
    connect_str,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0
)

# quick test
with engine.connect() as conn:
    print(conn.execute(text("SELECT 1")).fetchone())


print("=" * 60)
print("DATA MART ETL: Warehouse → Research Operations Data Mart")
print("=" * 60)

# ==============================================================================
# EXTRACT: Read from warehouse
# ==============================================================================

print("\nExtracting data from warehouse...")

query = """
SELECT 
    p.patient_id,
    p.age,
    p.age_group,
    p.gender,
    p.ethnicity,
    p.insurance_type,
    
    t.full_date as visit_date,
    v.total_cost,
    v.patient_satisfaction_score,
    v.readmission_30_days,
    v.adverse_event
    
FROM dim_patients p
LEFT JOIN fact_clinical_visits v ON p.patient_id = v.patient_id
LEFT JOIN dim_time t ON v.date_id = t.date_id
ORDER BY p.patient_id, t.full_date
"""

warehouse_data = pd.read_sql(query, engine)
print(f"✓ Extracted {len(warehouse_data)} visit records")

# ==============================================================================
# TRANSFORM: Aggregate to patient level
# ==============================================================================

print("\nTransforming to patient-level summaries...")

# Convert dates
warehouse_data['visit_date'] = pd.to_datetime(warehouse_data['visit_date'])

# Aggregate by patient
patient_summary = warehouse_data.groupby('patient_id').agg(
    # Demographics (take first - same for all visits)
    age=('age', 'first'),
    age_group=('age_group', 'first'),
    gender=('gender', 'first'),
    ethnicity=('ethnicity', 'first'),
    insurance_type=('insurance_type', 'first'),
    
    # Visit metrics
    total_visits=('visit_date', 'count'),
    first_visit_date=('visit_date', 'min'),
    last_visit_date=('visit_date', 'max'),
    
    # Financial metrics
    total_cost=('total_cost', 'sum'),
    
    # Quality metrics
    average_satisfaction_score=('patient_satisfaction_score', 'mean'),
    readmissions_30_day=('readmission_30_days', 'sum'),
    adverse_events_count=('adverse_event', 'sum')
).reset_index()

# Calculate days since last visit
today = datetime.now().date()
patient_summary['days_since_last_visit'] = (
    today - pd.to_datetime(patient_summary['last_visit_date']).dt.date
).apply(lambda x: x.days)

# Risk assessment
patient_summary['chronic_condition_count'] = (
    (patient_summary['total_visits'] >= 3).astype(int) + 
    (patient_summary['readmissions_30_day'] > 0).astype(int)
)

patient_summary['high_risk_patient'] = (
    (patient_summary['readmissions_30_day'] > 0) | 
    (patient_summary['adverse_events_count'] > 0) |
    (patient_summary['total_visits'] > 5)
).astype(int)

# Add timestamp
patient_summary['last_updated'] = datetime.now()

# Round decimals
patient_summary['average_satisfaction_score'] = patient_summary['average_satisfaction_score'].round(1)
patient_summary['total_cost'] = patient_summary['total_cost'].round(2)

print(f"✓ Aggregated to {len(patient_summary)} patient summaries")

# ==============================================================================
# LOAD: Insert into data mart
# ==============================================================================

print("\nLoading into research_operations data mart...")

try:
    # Load patient summaries
    patient_summary.to_sql(
        'fact_patient_summary', 
        engine, 
        schema='research_operations',
        if_exists='append',  # Replace existing data
        index=False
    )
    print(f"✓ Loaded {len(patient_summary)} patient summaries")
    
    # ==============================================================================
    # Create sample intervention data
    # ==============================================================================
    
    print("\nCreating sample intervention programs...")
    
    interventions = pd.DataFrame([
        {'intervention_name': 'Diabetes Management Program', 'intervention_type': 'Preventive', 'target_population': 'Type 2 Diabetes patients'},
        {'intervention_name': 'Cardiac Rehabilitation', 'intervention_type': 'Treatment', 'target_population': 'Heart disease patients'},
        {'intervention_name': 'High-Risk Patient Monitoring', 'intervention_type': 'Follow-up', 'target_population': 'Patients with readmissions'},
        {'intervention_name': 'Mental Health Support Group', 'intervention_type': 'Preventive', 'target_population': 'Depression/Anxiety patients'},
        {'intervention_name': 'Medication Adherence Program', 'intervention_type': 'Follow-up', 'target_population': 'Chronic condition patients'}
    ])
    
    interventions.to_sql(
        'dim_interventions',
        engine,
        schema='research_operations',
        if_exists='append',
        index=False
    )
    print(f"✓ Loaded {len(interventions)} intervention programs")
    
    # Create sample care teams
    print("\nCreating sample care teams...")
    
    care_teams = pd.DataFrame([
        {'team_name': 'Primary Care Team A', 'specialty': 'Primary Care', 'facility_name': 'University Medical Center'},
        {'team_name': 'Cardiology Team', 'specialty': 'Cardiology', 'facility_name': 'Regional Trauma Center'},
        {'team_name': 'Oncology Team', 'specialty': 'Oncology', 'facility_name': 'Academic Research Hospital'},
        {'team_name': 'Mental Health Team', 'specialty': 'Psychiatry', 'facility_name': 'Community General Hospital'},
        {'team_name': 'Emergency Care Team', 'specialty': 'Emergency Medicine', 'facility_name': 'Regional Trauma Center'}
    ])
    
    care_teams.to_sql(
        'dim_care_teams',
        engine,
        schema='research_operations',
        if_exists='append',
        index=False
    )
    print(f"✓ Loaded {len(care_teams)} care teams")
    
    print("\n" + "=" * 60)
    print("DATA MART ETL COMPLETE ✓")
    print("=" * 60)
    
    # Summary statistics
    print("\nData Mart Summary:")
    print(f"Total Patients: {len(patient_summary)}")
    print(f"High-Risk Patients: {patient_summary['high_risk_patient'].sum()}")
    print(f"Average Visits per Patient: {patient_summary['total_visits'].mean():.1f}")
    print(f"Patients with Readmissions: {(patient_summary['readmissions_30_day'] > 0).sum()}")
    print(f"Average Patient Satisfaction: {patient_summary['average_satisfaction_score'].mean():.1f}/10")
    
except Exception as e:
    print(f"\nERROR: {e}")
    raise
