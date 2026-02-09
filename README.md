# Bluevia Hands-On

## What is this?

This repo is for **getting set up before the interview**: get the data and run everything locally (however you like). Install whatever dependencies you need. Please don’t try to solve the task or write code for it beforehand—the actual prompt will be given live. The task will be about **sepsis**; a bit of light reading on it beforehand may help. This repo is just here so you can hit the ground running.

The dataset is a **1,163-patient synthetic EHR** modeled after the schema and coding conventions used by large health systems like Mayo Clinic. It includes realistic (but entirely fictional) patient medical histories: demographics, encounters, diagnoses, labs, vitals, medications, procedures, and claims.

**Important:** All data is synthetic. No real patient information is contained here.

## Pre-Interview Setup

**1. Extract the data**

```bash
python scripts/unzip_data.py   # extracts data/synthetic_1k.zip → data/raw/*.csv
```

**2. Dependencies (your choice)**

Use whatever stack you’re comfortable with. Common options:

- **pandas** — tabular data and joins
- **scikit-learn** — feature engineering, models, evaluation
- **PyTorch** — if you really want to train a neural net in 60 minutes, we won’t stop you 🙂

No strict requirements; install what you need.

## Quick start

```python
import pandas as pd

patients = pd.read_csv("data/raw/patients.csv")
conditions = pd.read_csv("data/raw/conditions.csv")
encounters = pd.read_csv("data/raw/encounters.csv")
observations = pd.read_csv("data/raw/observations.csv")
```

---

## Dataset at a Glance

| File | Rows | Size | Description |
|------|-----:|-----:|-------------|
| `patients.csv` | 1,163 | 330 KB | Patient demographics (1,000 alive, 163 deceased) |
| `encounters.csv` | 61,459 | 18 MB | All visit/encounter records |
| `conditions.csv` | 38,094 | 4.8 MB | Diagnosis records (SNOMED-CT) |
| `observations.csv` | 531,144 | 88 MB | Labs, vitals, surveys (LOINC) |
| `medications.csv` | 56,430 | 13 MB | Medication orders (RxNorm) |
| `procedures.csv` | 83,823 | 15 MB | Procedures performed (SNOMED-CT) |
| `careplans.csv` | 3,931 | 740 KB | Care plan records |
| `allergies.csv` | 794 | 139 KB | Allergy records |
| `immunizations.csv` | 17,009 | 2.4 MB | Immunization records (CVX) |
| `imaging_studies.csv` | 151,637 | 50 MB | Imaging study metadata |
| `claims.csv` | 117,889 | 40 MB | Insurance claim headers |
| `claims_transactions.csv` | 711,238 | 296 MB | Line-item claim transactions |
| `organizations.csv` | 1,127 | 152 KB | Healthcare organizations |
| `providers.csv` | 5,056 | 886 KB | Individual clinicians |
| `payers.csv` | 10 | 2.2 KB | Insurance payers |
| `payer_transitions.csv` | 53,101 | 8.6 MB | Insurance coverage changes over time |
| `devices.csv` | 89 | 20 KB | Patient-affixed devices |
| `supplies.csv` | 1,573 | 221 KB | Supplies used in care delivery |

**Total:** ~1.8M rows across 18 CSV files, ~530 MB on disk.

---

## Table Schemas

### patients.csv

The anchor table. Every other clinical table references patients via a `PATIENT` foreign key.

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Primary key |
| BIRTHDATE | Date | `YYYY-MM-DD` |
| DEATHDATE | Date | Date of death (null if alive) |
| SSN | String | Social Security Number (synthetic) |
| DRIVERS | String | Driver's license ID |
| PASSPORT | String | Passport ID |
| PREFIX | String | Name prefix (Mr., Mrs., Dr.) |
| FIRST | String | First name |
| LAST | String | Last name |
| SUFFIX | String | Name suffix (PhD, MD) |
| MAIDEN | String | Maiden name |
| MARITAL | String | Marital status (`M` or `S`) |
| RACE | String | Primary race |
| ETHNICITY | String | Primary ethnicity |
| GENDER | String | `M` or `F` |
| BIRTHPLACE | String | Town, State, Country |
| ADDRESS | String | Street address |
| CITY | String | City |
| STATE | String | State |
| COUNTY | String | County |
| ZIP | String | Zip code |
| LAT | Numeric | Latitude |
| LON | Numeric | Longitude |
| HEALTHCARE_EXPENSES | Numeric | Lifetime healthcare cost to patient |
| HEALTHCARE_COVERAGE | Numeric | Lifetime amount covered by payers |

### encounters.csv

Every clinical event (condition, observation, medication, procedure) links to an encounter. This is the **temporal window** for phenotyping.

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Primary key |
| START | ISO 8601 UTC | Encounter start datetime |
| STOP | ISO 8601 UTC | Encounter end datetime |
| PATIENT | UUID | FK to `patients.Id` |
| ORGANIZATION | UUID | FK to `organizations.Id` |
| PROVIDER | UUID | FK to `providers.Id` |
| PAYER | UUID | FK to `payers.Id` |
| ENCOUNTERCLASS | String | `ambulatory`, `emergency`, `inpatient`, `wellness`, `urgentcare` |
| CODE | String | SNOMED-CT encounter code |
| DESCRIPTION | String | Encounter type description |
| BASE_ENCOUNTER_COST | Numeric | Base cost (excludes line items) |
| TOTAL_CLAIM_COST | Numeric | Total cost including line items |
| PAYER_COVERAGE | Numeric | Amount covered by payer |
| REASONCODE | String | SNOMED-CT diagnosis code triggering the encounter |
| REASONDESCRIPTION | String | Reason description |

**Encounter class distribution in this dataset:**
- wellness: 24,038
- ambulatory: 20,124
- outpatient: 10,837
- urgentcare: 2,564
- emergency: 2,168
- **inpatient: 1,728** (critical for phenotyping)

### conditions.csv

Diagnosis records coded in SNOMED-CT. Maps to ICD-10 diagnoses in real EHR data.

| Column | Type | Description |
|--------|------|-------------|
| START | Date | Diagnosis date (`YYYY-MM-DD`) |
| STOP | Date | Resolution date (null if ongoing) |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | SNOMED-CT diagnosis code |
| DESCRIPTION | String | Condition description |

### observations.csv

The **largest clinical table**. Contains labs, vitals, survey scores, and exam findings coded in LOINC.

| Column | Type | Description |
|--------|------|-------------|
| DATE | ISO 8601 UTC | Observation datetime |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CATEGORY | String | `laboratory`, `vital-signs`, `survey`, `exam`, `procedure`, `social-history`, `imaging`, `therapy` |
| CODE | String | LOINC code |
| DESCRIPTION | String | Observation name |
| VALUE | String | Recorded value (numeric or text) |
| UNITS | String | Units of measure |
| TYPE | String | `numeric` or `text` |

**Category breakdown:**
- survey: 218,284
- laboratory: 163,502
- vital-signs: 116,274
- exam/procedure/other: ~1,084

### medications.csv

Medication orders coded in RxNorm.

| Column | Type | Description |
|--------|------|-------------|
| START | ISO 8601 UTC | Prescription start |
| STOP | ISO 8601 UTC | Prescription end (null if ongoing) |
| PATIENT | UUID | FK to `patients.Id` |
| PAYER | UUID | FK to `payers.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | RxNorm medication code |
| DESCRIPTION | String | Medication name/description |
| BASE_COST | Numeric | Cost per dispense |
| PAYER_COVERAGE | Numeric | Amount covered per dispense |
| DISPENSES | Numeric | Number of fills |
| TOTALCOST | Numeric | Total cost across all fills |
| REASONCODE | String | SNOMED-CT code for the indication |
| REASONDESCRIPTION | String | Indication description |

### procedures.csv

Procedures coded in SNOMED-CT. Includes both clinical assessments and surgical procedures.

| Column | Type | Description |
|--------|------|-------------|
| START | ISO 8601 UTC | Procedure start |
| STOP | ISO 8601 UTC | Procedure end |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | SNOMED-CT procedure code |
| DESCRIPTION | String | Procedure description |
| BASE_COST | Numeric | Procedure cost |
| REASONCODE | String | SNOMED-CT indication code |
| REASONDESCRIPTION | String | Indication description |

### careplans.csv

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Primary key |
| START | Date | Care plan start date |
| STOP | Date | Care plan end date |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | SNOMED-CT code |
| DESCRIPTION | String | Care plan description |
| REASONCODE | String | SNOMED-CT indication code |
| REASONDESCRIPTION | String | Indication description |

### allergies.csv

| Column | Type | Description |
|--------|------|-------------|
| START | Date | Allergy onset date |
| STOP | Date | Allergy end date |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | Allergy code (SNOMED-CT or RxNorm) |
| SYSTEM | String | Code system (`SNOMED-CT` or `RxNorm`) |
| DESCRIPTION | String | Allergy description |
| TYPE | String | `allergy` or `intolerance` |
| CATEGORY | String | `drug`, `food`, or `environment` |
| REACTION1/2 | String | SNOMED-CT reaction codes |
| DESCRIPTION1/2 | String | Reaction descriptions |
| SEVERITY1/2 | String | `MILD`, `MODERATE`, or `SEVERE` |

### immunizations.csv

| Column | Type | Description |
|--------|------|-------------|
| DATE | ISO 8601 UTC | Administration date |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| CODE | String | CVX vaccine code |
| DESCRIPTION | String | Vaccine description |
| BASE_COST | Numeric | Cost |

### imaging_studies.csv

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Study identifier |
| DATE | ISO 8601 UTC | Study date |
| PATIENT | UUID | FK to `patients.Id` |
| ENCOUNTER | UUID | FK to `encounters.Id` |
| SERIES_UID | String | DICOM series UID |
| BODYSITE_CODE | String | SNOMED body site code |
| BODYSITE_DESCRIPTION | String | Body site |
| MODALITY_CODE | String | DICOM modality code |
| MODALITY_DESCRIPTION | String | Modality (CT, MRI, X-ray, etc.) |
| INSTANCE_UID | String | DICOM instance UID |
| SOP_CODE | String | DICOM SOP class code |
| SOP_DESCRIPTION | String | SOP description |
| PROCEDURE_CODE | String | SNOMED-CT procedure code |

### claims.csv / claims_transactions.csv

Insurance billing data. Claims link to encounters; transactions are line items within each claim. These are the two largest files by disk size (296 MB + 40 MB) due to the volume of financial transactions.

### organizations.csv / providers.csv

Reference tables for healthcare organizations (hospitals, clinics) and individual clinicians.

### payers.csv / payer_transitions.csv

Insurance payer reference data and patient coverage history over time.

### devices.csv / supplies.csv

Patient-affixed devices (e.g., cardiac pacemakers) and supplies used during care delivery.

---

## Data Model (Join Keys)

```
patients.Id
  ├── encounters.PATIENT ──→ encounters.Id
  │     ├── conditions.ENCOUNTER
  │     ├── observations.ENCOUNTER
  │     ├── medications.ENCOUNTER
  │     ├── procedures.ENCOUNTER
  │     ├── careplans.ENCOUNTER
  │     ├── allergies.ENCOUNTER
  │     ├── immunizations.ENCOUNTER
  │     ├── imaging_studies.ENCOUNTER
  │     ├── devices.ENCOUNTER
  │     └── supplies.ENCOUNTER
  ├── claims.PATIENTID ──→ claims.Id
  │     └── claims_transactions.CLAIMID
  └── payer_transitions.PATIENT
```

All foreign keys are clean in this dataset (zero orphan references).

---

## Terminology Systems

| Domain | Code System | Used In |
|--------|-------------|---------|
| Diagnoses | SNOMED-CT | conditions, encounters (REASONCODE) |
| Labs / Vitals | LOINC | observations |
| Medications | RxNorm | medications |
| Procedures | SNOMED-CT | procedures |
| Vaccines | CVX | immunizations |
| Body Sites | SNOMED-CT | imaging_studies |
| Imaging Modality | DICOM-DCM | imaging_studies |

In real EHR data from Mayo Clinic, expect a mix of ICD-10-CM (diagnoses), CPT/HCPCS (procedures), and institution-specific local codes that will need vocabulary mapping.
