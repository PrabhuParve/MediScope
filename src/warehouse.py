"""SQLite star-schema warehouse and ETL for encounter-level diabetes analytics.
The source dataset contains no encounter date, so this warehouse intentionally has no Dim_Date.
"""
from pathlib import Path
import sqlite3
import pandas as pd
from src.common import ROOT, load_clean

DB_PATH = ROOT / 'data' / 'warehouse' / 'mediscope_warehouse.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DIMS = {
 'Dim_Patient': ['patient_nbr','race','gender','age'],
 'Dim_Admission': ['admission_type_id','admission_source_id'],
 'Dim_Discharge': ['discharge_disposition_id'],
 'Dim_Diagnosis': ['diag_1','diag_2','diag_3','number_diagnoses'],
 'Dim_Medication': ['insulin','metformin','glipizide','glyburide','pioglitazone','rosiglitazone','diabetesMed','change'],
}

def build_warehouse():
    df = load_clean().copy()
    # Keep one dimension record per unique business-key combination.
    conn = sqlite3.connect(DB_PATH)
    try:
        for table, cols in DIMS.items():
            dim = df[cols].drop_duplicates().reset_index(drop=True)
            dim.insert(0, table.lower() + '_key', range(1, len(dim)+1))
            dim.to_sql(table, conn, if_exists='replace', index=False)
        # Create key lookups using the exact natural-key combinations used above.
        natural_keys = list(dict.fromkeys(col for cols in DIMS.values() for col in cols))
        measures = ['time_in_hospital','num_lab_procedures','num_procedures','num_medications',
                    'number_outpatient','number_emergency','number_inpatient','readmitted']
        fact = df[['encounter_id'] + natural_keys + measures].copy()
        fact.rename(columns={'encounter_id':'encounter_id_nk'}, inplace=True)
        for table, cols in DIMS.items():
            dim = df[cols].drop_duplicates().reset_index(drop=True)
            keycol = table.lower() + '_key'
            dim[keycol] = range(1, len(dim)+1)
            lookup = dim[cols + [keycol]]
            fact = fact.merge(lookup, on=cols, how='left', validate='many_to_one')
        fact.rename(columns={'encounter_id_nk':'encounter_id'}, inplace=True)
        fact.insert(0, 'fact_encounter_key', range(1, len(fact)+1))
        fact.to_sql('Fact_Encounter', conn, if_exists='replace', index=False)
        conn.execute('CREATE INDEX IF NOT EXISTS idx_fact_patient ON Fact_Encounter(dim_patient_key)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_fact_readmitted ON Fact_Encounter(readmitted)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_fact_admission ON Fact_Encounter(dim_admission_key)')
        conn.commit()
        summary = pd.read_sql_query("SELECT 'Fact_Encounter' table_name, COUNT(*) row_count FROM Fact_Encounter UNION ALL " +
            "SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) FROM sqlite_master m WHERE type='table' AND name LIKE 'Dim_%'", conn)
        summary.to_csv(ROOT/'outputs'/'tables'/'warehouse_table_summary.csv', index=False)
        return {'database': str(DB_PATH), 'fact_rows': len(fact), 'dimension_rows': {t: int(pd.read_sql_query(f'SELECT COUNT(*) n FROM {t}',conn).iloc[0,0]) for t in DIMS}}
    finally:
        conn.close()

if __name__ == '__main__':
    print(build_warehouse())
