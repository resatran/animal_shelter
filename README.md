# Animal Shelter Data Pipeline

## Overview
This repository contains data cleaning and preprocessing for an animal shelter dataset from the Austin Animal Center in Austin, Texas. The work prepares intake and outcome records for downstream analysis and modeling.

**Data Sources:**  
- Intake Data: https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data  
- Outcome Data: https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data  

**Project Overview**  
- **Goal:** Clean and structure the dataset to improve readability and usability, with the objective of analyzing how long animals typically stay in the shelter and estimating time to adoption.  
- **Methods:** Merged intake and outcome datasets to create a unified master dataset, followed by data cleaning, column standardization, and datetime feature engineering. The cleaned dataset is designed to support analysis across variables such as breed, age, and intake conditions.  
- **Scope:** Developed a reproducible data pipeline that produces a clean, standardized dataset for downstream analysis, ensuring consistency and preserving relationships between intake and outcome records.  
- **Collaboration:** Conducted as part of a research project under UCSB Statistics Professor Tianyu Zhang.  

---

## Final Dataset

The final cleaned dataset is located in:

`data/processed/cleaned_animal_data.csv`

### Main Attributes
- `animal_id` – Unique identifier for each animal  
- `name` – Name of the animal (if available)  
- `date_intake` – Date the animal entered the shelter  
- `date_outcome` – Date the animal left the shelter  
- `time_intake` – Time of intake  
- `time_outcome` – Time of outcome  
- `date_diff_days` – Length of stay in the shelter (in days), calculated as the difference between intake and outcome dates  
- `animal_type` – Type of animal (e.g., dog, cat)  
- `breed` – Breed of the animal  
- `age_year` – Age of the animal at intake (in years)  
- `intake_type` – Method of intake (e.g., stray, owner surrender)  
- `outcome_type` – Outcome category (e.g., adoption, transfer, euthanasia)  
- `sex_upon_outcome` – Sex of the animal at the time of outcome  
- `intake_condition` – Condition of the animal at intake  
- `date_of_birth` – Reported date of birth of the animal  

This dataset is fully cleaned and standardized, and serves as the primary input for downstream analysis and modeling.

---

## Features
- Load and save datasets efficiently
- Standardize column names (lowercase, underscore format)
- Clean inconsistent and missing values
- Split datetime columns into usable features (date, time)
- Reproducible and organized data workflow

---

## Design Decisions
- **Merge Before Cleaning:** Intake and outcome datasets were merged prior to cleaning to preserve relationships between records. Cleaning datasets separately could introduce inconsistencies or mismatches, so merging first ensured transformations were applied uniformly across linked data.

- **Column Standardization:** Converted all column names to lowercase with underscores to ensure consistency and prevent errors in downstream analysis.

- **Datetime Splitting:** Separated datetime fields into components (date, time) to support feature engineering and time-based analysis.

- **Modular Functions:** Built reusable functions (e.g., `load_csv`, `save_csv`) to make the pipeline scalable and maintainable.

- **Structured File Organization:** Separated raw and processed data to preserve original datasets and support reproducibility.

---

## Project Structure
```bash
animal_data/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── load_save.py
│   ├── cleaning.py
│   └── datetime_split.py
│
├── notebooks/
│
└── README.md
```

---

## Key Functions
- `load_csv()` – loads raw data into a DataFrame  
- `save_csv()` – saves cleaned data  
- `split_datetime_intake()` – extracts structured time features  
- `standardize_column()` – formats column names consistently  

---

## How to Use
1. Place raw datasets in `data/raw/`
2. Run the cleaning scripts or notebook
3. Processed data will be saved in `data/processed/`

---

## Future Improvements
- Add exploratory data analysis (EDA)
- Build predictive models (e.g., adoption likelihood)
- Create visual dashboards
