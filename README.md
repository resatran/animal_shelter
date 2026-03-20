# Animal Shelter Data Pipeline

## Overview
This project builds a data cleaning and preprocessing pipeline for animal shelter intake and outcome data. The goal is to transform raw, messy datasets into a clean, standardized format that can be used for analysis and modeling.

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
