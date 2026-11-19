# MediScope — Diabetes Patient Analytics & Hospital Readmission Analysis

**MDM academic project | Python 3.11 | SQLite | Streamlit | Plotly**

MediScope demonstrates data preparation, exploratory analytics, a relational star-schema data warehouse, OLAP operations, decision-tree classification, association-rule mining and regression using the UCI Diabetes 130-US Hospitals encounter dataset.

> **Academic-use notice:** This project is for educational data-management and analytics demonstration only. It is not a clinical decision-support system and must not be used to diagnose, treat, triage or make decisions about patients.

## 1. What's included

- Data cleaning, profiling, missing-value and quality reports.
- Exploratory analysis and interactive visualizations.
- SQLite data warehouse populated through a repeatable Python ETL process.
- Star schema: `Fact_Encounter` plus `Dim_Patient`, `Dim_Admission`, `Dim_Discharge`, `Dim_Diagnosis`, and `Dim_Medication`.
- OLAP: roll-up, drill-down, slice, dice and pivot, implemented with SQL/Pandas.
- Educational ID3 (information gain), C4.5-style (gain ratio) and Gini-based decision tree comparison.
- Apriori with vertical TID-set intersections and recursive FP-Growth using conditional pattern bases/conditional FP-trees.
- Association-rule support, confidence and lift; medication hierarchy example.
- Multiple linear regression and model evaluation.
- Streamlit dashboard with interactive Plotly charts and an OLAP explorer.

## 2. Project layout

```text
MediScope_Full_Project/
├── data/
│   ├── raw/diabetic_data.csv
│   ├── processed/diabetic_data_cleaned.csv
│   └── warehouse/mediscope_warehouse.db
├── src/
│   ├── common.py
│   ├── prepare_data.py
│   ├── eda.py
│   ├── decision_trees.py
│   ├── association_rules.py
│   ├── regression.py
│   ├── warehouse.py
│   ├── olap.py
│   └── run_all.py
├── outputs/
│   ├── figures/
│   └── tables/
├── models/
├── docs/
├── app.py
├── requirements.txt
└── README.md
```

## 3. Windows installation (no Docker required)

Install Python 3.11 and open PowerShell in the folder containing `requirements.txt`.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use the interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No Docker, MySQL, PostgreSQL or separate database server is needed. SQLite is included with Python.

## 4. Run the complete pipeline

From the project root:

```powershell
py -3.11 -m src.run_all
```

The pipeline runs cleaning, EDA, decision trees, association mining, regression, warehouse ETL and OLAP export. Generated outputs are saved under `outputs/`, `models/` and `data/warehouse/`.

To run individual modules:

```powershell
py -3.11 -m src.prepare_data
py -3.11 -m src.eda
py -3.11 -m src.decision_trees
py -3.11 -m src.association_rules
py -3.11 -m src.regression
py -3.11 -m src.warehouse
py -3.11 -m src.olap
```

## 5. Launch the dashboard

```powershell
py -3.11 -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. Keep the PowerShell terminal open while using the dashboard. Stop the server with `Ctrl+C`.

## 6. Warehouse design and grain

The fact-table grain is **one row per source hospital encounter**. `encounter_id` is retained as a source/natural identifier; generated integer surrogate keys connect each fact row to its descriptive dimensions. Numeric encounter measures include length of stay, lab procedures, procedures, medications and prior outpatient/emergency/inpatient visit counts. `readmitted` is retained as an outcome attribute for analysis.

| Table | Role | Contents |
|---|---|---|
| `Fact_Encounter` | Fact | One row per encounter; measures and dimension foreign keys |
| `Dim_Patient` | Dimension | Patient identifier, race, gender and age band |
| `Dim_Admission` | Dimension | Admission type and admission source IDs |
| `Dim_Discharge` | Dimension | Discharge disposition ID |
| `Dim_Diagnosis` | Dimension | Three diagnosis fields and diagnosis count |
| `Dim_Medication` | Dimension | Selected medication status fields, diabetes-medication flag and change flag |

**Date-dimension limitation:** the supplied source file does not contain an encounter date/time column. Therefore this implementation intentionally does not fabricate `Dim_Date`. If a date-bearing source is added later, a proper calendar dimension can be introduced.

## 7. OLAP operations

- **Roll-up:** summarizes encounters by admission type.
- **Drill-down:** expands admission summaries by admission source and discharge disposition; can be filtered to one admission type.
- **Slice:** filters the cube to one readmission category.
- **Dice:** filters by a combination of admission type and readmission category.
- **Pivot:** rotates the readmission category into columns for comparison by admission type.

These are implemented in `src/olap.py` and exposed on the dashboard's **Data Warehouse & OLAP** page. CSV exports are also written to `outputs/tables/`.

## 8. Algorithm notes and limitations

- ID3 uses entropy/information gain over categorical multiway splits.
- C4.5-style uses gain ratio over categorical multiway splits. This is an educational subset, not the full C4.5 system (for example, continuous-threshold handling and pruning are not implemented).
- The custom `CART_gini` experiment uses Gini impurity but categorical multiway splits. Strict textbook CART uses binary splits; therefore the label is explicitly described as Gini-based/CART-style, not a complete canonical CART implementation.
- Apriori uses frequent-itemset candidate generation and vertical transaction-ID intersections for support counts.
- FP-Growth builds an FP-tree and recursively mines conditional pattern bases and conditional FP-trees. The supplied experiment is bounded by the transaction sample and chosen support threshold.
- Regression predicts `time_in_hospital`; it is an educational association/prediction exercise, not a causal model.
- Patient-group splitting is used where applicable to reduce leakage across repeated encounters from the same patient.

## 9. Data cleaning and interpretation

The raw CSV is preserved unchanged. The preparation step strips whitespace, converts source `?` placeholders to missing values, removes exact duplicate rows, excludes the highly incomplete `weight`, `payer_code` and `medical_specialty` columns from the analytical extract, and fills missing categorical/diagnosis values with `Unknown`. Numeric missingness is not indiscriminately imputed. Quality and profile reports are saved under `outputs/tables/`.

The resulting cleaned file is a reproducible analytical extract, not a claim that every source-data issue has been resolved. Identifiers remain available for joins and group-based splitting but should not be used as predictive input features.

## 10. Key outputs

- `outputs/tables/data_quality_report.csv`
- `outputs/tables/missing_value_report.csv`
- `outputs/tables/dataset_profile.csv`
- `outputs/tables/decision_tree_comparison.csv`
- `outputs/tables/apriori_rules.csv`
- `outputs/tables/fp_growth_itemsets.csv`
- `outputs/tables/multilevel_itemsets.csv`
- `outputs/tables/regression_metrics.csv`
- `outputs/tables/olap_*.csv`
- `data/warehouse/mediscope_warehouse.db`

## 11. Dataset and responsible use

The project uses the Diabetes 130-US Hospitals dataset. A row represents an encounter, not necessarily a unique person; a patient may have multiple encounters. The readmission categories (`NO`, `>30`, `<30`) are retained from the source. Observed associations do not establish causation, and the dataset's limitations should be discussed in any academic report or presentation.
