"""
Healthcare BI Solution - Synthetic Clinical Visits Data Generator
Output: 5,000+ patient visits with realistic diagnosis-treatment-outcomes
"""

# Install packages
import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set working directory
os.chdir("/Users/nadia/Documents/GitHub - n7dia/healthcare-bi-solution/")

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)


# ==============================================================================
# Clinical Patterns - Realistic diagnosis, treatment, and outcome mappings
# ==============================================================================

CLINICAL_PATTERNS = {
    'Type 2 Diabetes': {
        'treatments': ['Metformin', 'Insulin Therapy', 'Lifestyle Modification Program', 'Combination Therapy'],
        'cost_range': (1500, 8000),
        'los_range': (0, 2),
        'success_rate': 0.72,
        'icd10': 'E11'
    },
    'Hypertension': {
        'treatments': ['ACE Inhibitors', 'Beta Blockers', 'Calcium Channel Blockers', 'Lifestyle Changes'],
        'cost_range': (1000, 4500),
        'los_range': (0, 1),
        'success_rate': 0.78,
        'icd10': 'I10'
    },
    'Depression': {
        'treatments': ['SSRI Medication', 'Cognitive Behavioral Therapy', 'Counseling', 'Combination Therapy'],
        'cost_range': (800, 5000),
        'los_range': (0, 0),
        'success_rate': 0.68,
        'icd10': 'F33'
    },
    'Generalized Anxiety Disorder': {
        'treatments': ['Anxiolytic Medication', 'Cognitive Behavioral Therapy', 'Counseling', 'Relaxation Techniques'],
        'cost_range': (900, 4800),
        'los_range': (0, 0),
        'success_rate': 0.70,
        'icd10': 'F41.1'
    },
    'Asthma': {
        'treatments': ['Inhaled Corticosteroids', 'Bronchodilators', 'Combination Inhaler', 'Allergen Avoidance'],
        'cost_range': (600, 3500),
        'los_range': (0, 1),
        'success_rate': 0.82,
        'icd10': 'J45'
    },
    'Coronary Artery Disease': {
        'treatments': ['Stent Placement', 'CABG Surgery', 'Medication Management', 'Cardiac Rehabilitation'],
        'cost_range': (25000, 85000),
        'los_range': (2, 7),
        'success_rate': 0.75,
        'icd10': 'I25.1'
    },
    'COPD': {
        'treatments': ['Bronchodilators', 'Inhaled Steroids', 'Oxygen Therapy', 'Pulmonary Rehabilitation'],
        'cost_range': (3000, 12000),
        'los_range': (1, 5),
        'success_rate': 0.65,
        'icd10': 'J44'
    },
    'Pneumonia': {
        'treatments': ['Antibiotics IV', 'Antibiotics Oral', 'Oxygen Therapy', 'Supportive Care'],
        'cost_range': (8000, 25000),
        'los_range': (3, 7),
        'success_rate': 0.85,
        'icd10': 'J18'
    },
    'Osteoarthritis': {
        'treatments': ['NSAIDs', 'Physical Therapy', 'Joint Injection', 'Joint Replacement'],
        'cost_range': (2000, 55000),
        'los_range': (0, 4),
        'success_rate': 0.70,
        'icd10': 'M19'
    },
    'Hip Fracture': {
        'treatments': ['Hip Replacement', 'Open Reduction Internal Fixation', 'Physical Therapy'],
        'cost_range': (40000, 80000),
        'los_range': (4, 8),
        'success_rate': 0.80,
        'icd10': 'S72.0'
    },
    'Acute Appendicitis': {
        'treatments': ['Laparoscopic Appendectomy', 'Open Appendectomy'],
        'cost_range': (20000, 45000),
        'los_range': (1, 3),
        'success_rate': 0.95,
        'icd10': 'K35'
    },
    'Breast Cancer': {
        'treatments': ['Lumpectomy + Radiation', 'Mastectomy', 'Chemotherapy', 'Hormone Therapy'],
        'cost_range': (50000, 150000),
        'los_range': (1, 5),
        'success_rate': 0.72,
        'icd10': 'C50'
    },
    'Colorectal Cancer': {
        'treatments': ['Surgical Resection', 'Chemotherapy', 'Radiation Therapy', 'Combination Therapy'],
        'cost_range': (60000, 180000),
        'los_range': (5, 10),
        'success_rate': 0.68,
        'icd10': 'C18'
    },
    'Migraine': {
        'treatments': ['Triptans', 'Preventive Medication', 'Botox Injections', 'Lifestyle Modifications'],
        'cost_range': (500, 3500),
        'los_range': (0, 0),
        'success_rate': 0.65,
        'icd10': 'G43'
    },
    'Lower Back Pain': {
        'treatments': ['Physical Therapy', 'Pain Management', 'Epidural Injection', 'Surgery'],
        'cost_range': (1500, 35000),
        'los_range': (0, 3),
        'success_rate': 0.62,
        'icd10': 'M54.5'
    },
    'Cellulitis': {
        'treatments': ['Antibiotics Oral', 'Antibiotics IV', 'Wound Care'],
        'cost_range': (1200, 8000),
        'los_range': (0, 4),
        'success_rate': 0.88,
        'icd10': 'L03'
    },
    'Urinary Tract Infection': {
        'treatments': ['Antibiotics Oral', 'Antibiotics IV', 'Increased Hydration'],
        'cost_range': (500, 4000),
        'los_range': (0, 2),
        'success_rate': 0.90,
        'icd10': 'N39.0'
    },
    'Acute Bronchitis': {
        'treatments': ['Supportive Care', 'Bronchodilators', 'Cough Suppressants'],
        'cost_range': (300, 1500),
        'los_range': (0, 0),
        'success_rate': 0.85,
        'icd10': 'J20'
    },
    'Gastroesophageal Reflux Disease': {
        'treatments': ['Proton Pump Inhibitors', 'H2 Blockers', 'Lifestyle Modifications', 'Fundoplication'],
        'cost_range': (800, 25000),
        'los_range': (0, 2),
        'success_rate': 0.75,
        'icd10': 'K21'
    },
    'Atrial Fibrillation': {
        'treatments': ['Rate Control Medication', 'Rhythm Control Medication', 'Ablation', 'Anticoagulation'],
        'cost_range': (5000, 45000),
        'los_range': (1, 4),
        'success_rate': 0.70,
        'icd10': 'I48'
    }
}


# ==============================================================================
# AGE-APPROPRIATE CONDITIONS
# ==============================================================================

AGE_CONDITIONS = {
    (0, 12): ['Asthma', 'Acute Bronchitis', 'Pneumonia'],
    (13, 18): ['Asthma', 'Acute Bronchitis', 'Migraine', 'Lower Back Pain'],
    (19, 35): ['Generalized Anxiety Disorder', 'Depression', 'Migraine', 'Lower Back Pain', 'Cellulitis', 'Urinary Tract Infection'],
    (36, 50): ['Depression', 'Generalized Anxiety Disorder', 'Type 2 Diabetes', 'Hypertension', 'Migraine', 'Lower Back Pain', 'Osteoarthritis'],
    (51, 65): ['Type 2 Diabetes', 'Hypertension', 'Coronary Artery Disease', 'Osteoarthritis', 'COPD', 'Breast Cancer', 'Colorectal Cancer', 'Gastroesophageal Reflux Disease'],
    (66, 100): ['Coronary Artery Disease', 'COPD', 'Pneumonia', 'Hip Fracture', 'Osteoarthritis', 'Atrial Fibrillation', 'Colorectal Cancer', 'Urinary Tract Infection']
}


# ==============================================================================
# DEMOGRAPHIC DATA - Categories
# ==============================================================================

GENDERS = ['Male', 'Female', 'Non-binary']
GENDER_WEIGHTS = [0.49, 0.49, 0.02]

ETHNICITIES = ['White', 'Black', 'Hispanic', 'Asian', 'Indigenous', 'Other']
ETHNICITY_WEIGHTS = [0.55, 0.13, 0.18, 0.08, 0.04, 0.02]

INSURANCE_TYPES = ['Private Insurance', 'Medicare', 'Medicaid', 'Uninsured']
SOCIOECONOMIC_STATUS = ['Low', 'Medium', 'High']

FACILITIES = [
    'University Medical Center',
    'Community General Hospital',
    'Regional Trauma Center',
    'Suburban Clinic',
    'Academic Research Hospital'
]

FACILITY_TYPES = ['Hospital', 'Hospital', 'Hospital', 'Clinic', 'Hospital']

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_age_appropriate_diagnosis(age):
    """Return random diagnosis appropriate for patient age"""
    for age_range, conditions in AGE_CONDITIONS.items():
        if age_range[0] <= age <= age_range[1]:
            return random.choice(conditions)
    return 'Type 2 Diabetes'  # Default fallback

def calculate_outcome(pathway, age, has_insurance):
    """Calculate realistic outcome based on clinical factors"""
    base_success = pathway['success_rate']
    
    # Age adjustment (older = slightly worse outcomes)
    age_penalty = max(0, (age - 50) * 0.001)
    
    # Insurance adjustment (uninsured = worse outcomes)
    insurance_penalty = 0.05 if not has_insurance else 0
    
    # Comorbidity adjustment (random chance)
    comorbidity_penalty = 0.1 if random.random() < 0.15 else 0
    
    final_success_rate = base_success - age_penalty - insurance_penalty - comorbidity_penalty
    
    rand = random.random()
    if rand < final_success_rate:
        return random.choice(['Recovered', 'Improved'])
    elif rand < final_success_rate + 0.20:
        return 'Unchanged'
    else:
        return 'Worsened'

def calculate_readmission_risk(outcome, age, diagnosis):
    """Calculate if patient readmitted within 30 days"""
    base_risk = 0.10
    
    if outcome in ['Worsened', 'Unchanged']:
        base_risk += 0.15
    if age > 65:
        base_risk += 0.08
    if diagnosis in ['COPD', 'Coronary Artery Disease', 'Pneumonia']:
        base_risk += 0.12
    
    return random.random() < base_risk

def assign_insurance(age, ses):
    """Assign realistic insurance based on age and SES"""
    if age >= 65:
        return 'Medicare'
    elif ses == 'Low':
        if random.random() < 0.7:
            return 'Medicaid'
        else:
            return 'Uninsured'
    else:
        if random.random() < 0.85:
            return 'Private Insurance'
        else:
            return 'Medicaid'
          


def generate_visit_date(patient_num, total_patients):
    """Generate dates spread over 3 years"""
    start_date = datetime(2022, 1, 1)
    days_range = 365 * 3  # 3 years
    random_days = int((patient_num / total_patients) * days_range)
    return start_date + timedelta(days=random_days)


# ==============================================================================
# MAIN GENERATION FUNCTION
# ==============================================================================

def generate_clinical_data(num_patients=5000):
    """Generate realistic clinical visit dataset"""
    
    visits = []
    
    for i in range(num_patients):
        patient_id = f"P{100000 + i}"
        
        # Demographics
        age = int(np.random.beta(2, 5) * 85) + 1  # Realistic age distribution
        gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
        ethnicity = random.choices(ETHNICITIES, weights=ETHNICITY_WEIGHTS)[0]
        ses = random.choice(SOCIOECONOMIC_STATUS)
        insurance_type = assign_insurance(age, ses)
        
        # Clinical visit
        diagnosis = get_age_appropriate_diagnosis(age)
        pathway = CLINICAL_PATTERNS[diagnosis]
        
        treatment = random.choice(pathway['treatments'])
        
        # Cost with variation
        base_cost = random.uniform(*pathway['cost_range'])
        cost_variation = random.uniform(0.85, 1.15)  # ±15% variation
        cost = round(base_cost * cost_variation, 2)
        
        # Length of stay
        los_min, los_max = pathway['los_range']
        length_of_stay = random.randint(los_min, los_max)
        
        # Outcome
        has_insurance = insurance_type != 'Uninsured'
        outcome = calculate_outcome(pathway, age, has_insurance)
        
        # Readmission
        readmitted_30_days = calculate_readmission_risk(outcome, age, diagnosis)
        
        # Facility
        facility_idx = random.randint(0, len(FACILITIES) - 1)
        facility = FACILITIES[facility_idx]
        facility_type = FACILITY_TYPES[facility_idx]
        
        # Date
        visit_date = generate_visit_date(i, num_patients)
        
        # Patient satisfaction (1-10 scale, correlated with outcome)
        if outcome == 'Recovered':
            satisfaction = random.randint(8, 10)
        elif outcome == 'Improved':
            satisfaction = random.randint(6, 9)
        elif outcome == 'Unchanged':
            satisfaction = random.randint(4, 7)
        else:  # Worsened
            satisfaction = random.randint(1, 5)
        
        # Adverse event (rare but realistic)
        adverse_event = random.random() < 0.03
        
        visit = {
            'visit_id': i + 1,
            'patient_id': patient_id,
            'age': age,
            'gender': gender,
            'ethnicity': ethnicity,
            'socioeconomic_status': ses,
            'insurance_type': insurance_type,
            'visit_date': visit_date.strftime('%Y-%m-%d'),
            'facility_name': facility,
            'facility_type': facility_type,
            'diagnosis': diagnosis,
            'icd_10_code': pathway['icd10'],
            'treatment': treatment,
            'outcome': outcome,
            'length_of_stay_days': length_of_stay,
            'total_cost': cost,
            'readmission_30_days': 1 if readmitted_30_days else 0,
            'patient_satisfaction_score': satisfaction,
            'adverse_event': 1 if adverse_event else 0
        }
        
        visits.append(visit)
    
    return pd.DataFrame(visits)


# ==============================================================================
# GENERATE AND SAVE DATA
# ==============================================================================

# Only runs when you execute the script directly
if __name__ == "__main__":
    print("Generating synthetic clinical visit data...")
    print("=" * 60)
    
    # Generate main dataset
    df = generate_clinical_data(num_patients=5000)
    
    # Summary statistics
    print(f"\nGenerated {len(df)} clinical visits")
    print(f"Date range: {df['visit_date'].min()} to {df['visit_date'].max()}")
    print(f"\nAge distribution:")
    print(df['age'].describe())
    print(f"\nTop 5 diagnoses:")
    print(df['diagnosis'].value_counts().head())
    print(f"\nOutcome distribution:")
    print(df['outcome'].value_counts())
    print(f"\nAverage cost: ${df['total_cost'].mean():,.2f}")
    print(f"30-day readmission rate: {df['readmission_30_days'].mean():.1%}")
    
    # Save to CSV
    output_file = 'clinical_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Data saved to: {output_file}")
    print("=" * 60)
    
    # Display sample
    print("\nSample records:")
    print(df.head(10).to_string())

