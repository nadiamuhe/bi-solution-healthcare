"""
ETL: Load clinical visit data into Azure SQL warehouse
"""

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
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


print("Loading clinical visits data...")
df = pd.read_csv('clinical_data.csv')

print(f"Loaded {len(df)} visits")


# ==============================================================================
# TRANSFORM: Prepare dimension tables
# ==============================================================================

# Patients dimension
print("\nCreating dim_patients...")
patients = df[['patient_id', 'age', 'gender', 'ethnicity', 'socioeconomic_status', 'insurance_type']].copy()
patients['age_group'] = pd.cut(patients['age'], 
                               bins=[0, 18, 35, 50, 65, 100], 
                               labels=['0-18', '19-35', '36-50', '51-65', '66+'])
patients = patients.drop_duplicates(subset=['patient_id'])

# Diagnoses dimension
print("Creating dim_diagnoses...")
diagnoses = df[['diagnosis', 'icd_10_code']].copy()
diagnoses = diagnoses.rename(columns={'diagnosis': 'diagnosis_name'})
diagnoses['diagnosis_category'] = diagnoses['diagnosis_name'].apply(
    lambda x: 'Cardiovascular' if 'Heart' in x or 'Coronary' in x or 'Hypertension' in x or 'Atrial' in x
    else 'Respiratory' if 'COPD' in x or 'Asthma' in x or 'Pneumonia' in x or 'Bronchitis' in x
    else 'Mental Health' if 'Depression' in x or 'Anxiety' in x
    else 'Metabolic' if 'Diabetes' in x
    else 'Musculoskeletal' if 'Arthritis' in x or 'Fracture' in x or 'Back Pain' in x
    else 'Cancer' if 'Cancer' in x
    else 'Other'
)
diagnoses = diagnoses.drop_duplicates()
diagnoses = diagnoses.reset_index(drop=True)
diagnoses['diagnosis_id'] = diagnoses.index + 1

# Treatments dimension
print("Creating dim_treatments...")
treatments = df[['treatment']].copy()
treatments = treatments.rename(columns={'treatment': 'treatment_name'})
treatments['treatment_type'] = treatments['treatment_name'].apply(
    lambda x: 'Surgery' if any(word in x for word in ['Surgery', 'Appendectomy', 'Replacement', 'Resection', 'Lumpectomy', 'Mastectomy'])
    else 'Medication' if any(word in x for word in ['Medication', 'Antibiotics', 'SSRI', 'Metformin', 'Insulin', 'Inhibitor', 'Blocker'])
    else 'Therapy' if any(word in x for word in ['Therapy', 'Counseling', 'CBT', 'Rehabilitation'])
    else 'Procedure' if any(word in x for word in ['Stent', 'Injection', 'Ablation'])
    else 'Lifestyle' if 'Lifestyle' in x or 'Modifications' in x
    else 'Other'
)
treatments = treatments.drop_duplicates()
treatments = treatments.reset_index(drop=True)
treatments['treatment_id'] = treatments.index + 1

# Facilities dimension
print("Creating dim_facilities...")
facilities = df[['facility_name', 'facility_type']].copy()
facilities = facilities.drop_duplicates()
facilities = facilities.reset_index(drop=True)
facilities['facility_id'] = facilities.index + 1

# Time dimension
print("Creating dim_time...")
df['visit_date'] = pd.to_datetime(df['visit_date'])
dates = df[['visit_date']].drop_duplicates()
dates = dates.rename(columns={'visit_date': 'full_date'})
dates['year'] = dates['full_date'].dt.year
dates['quarter'] = dates['full_date'].dt.quarter
dates['month'] = dates['full_date'].dt.month
dates['month_name'] = dates['full_date'].dt.strftime('%B')
dates['day_of_week'] = dates['full_date'].dt.strftime('%A')
dates['date_id'] = dates['full_date'].dt.strftime('%Y%m%d').astype(int)
dates = dates.sort_values('full_date')

# ==============================================================================
# TRANSFORM: Create fact table with foreign keys
# ==============================================================================

print("\nCreating fact_clinical_visits...")
fact = df.copy()

# Join to get dimension IDs
fact = fact.merge(diagnoses[['diagnosis_name', 'diagnosis_id']], 
                  left_on='diagnosis', right_on='diagnosis_name', how='left')
fact = fact.merge(treatments[['treatment_name', 'treatment_id']], 
                  left_on='treatment', right_on='treatment_name', how='left')
fact = fact.merge(facilities[['facility_name', 'facility_id']], 
                  on='facility_name', how='left')

fact['visit_date'] = pd.to_datetime(fact['visit_date'])
fact['date_id'] = fact['visit_date'].dt.strftime('%Y%m%d').astype(int)

# Select final columns
fact = fact[[
    'visit_id', 'patient_id', 'diagnosis_id', 'treatment_id', 
    'facility_id', 'date_id', 'length_of_stay_days', 'total_cost',
    'readmission_30_days', 'patient_satisfaction_score', 
    'adverse_event', 'outcome'
]]

# ==============================================================================
# LOAD: Insert into Azure SQL
# ==============================================================================

print("\n" + "="*60)
print("LOADING DATA TO AZURE SQL DATABASE")
print("="*60)

try:
    print("\nLoading dim_patients...")
    patients.to_sql('dim_patients', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(patients)} patients")
    
    print("\nLoading dim_diagnoses...")
    diagnoses.drop(columns=['diagnosis_id']).to_sql('dim_diagnoses', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(diagnoses)} diagnoses")
    
    print("\nLoading dim_treatments...")
    treatments.drop(columns=['treatment_id']).to_sql('dim_treatments', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(treatments)} treatments")
    
    print("\nLoading dim_facilities...")
    facilities.drop(columns=['facility_id']).to_sql('dim_facilities', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(facilities)} facilities")
    
    print("\nLoading dim_time...")
    dates.to_sql('dim_time', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(dates)} dates")
    
    print("\nLoading fact_clinical_visits...")
    fact.to_sql('fact_clinical_visits', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(fact)} visits")
    
    print("\n" + "="*60)
    print("ETL COMPLETE ✓")
    print("="*60)
    
except Exception as e:
    print(f"\n ERROR: {e}")
    raise
  
  

