"""SQL-based OLAP operations over the MediScope star-schema warehouse."""
import sqlite3
import pandas as pd
from src.warehouse import DB_PATH, build_warehouse
from src.common import TABLES

def _conn():
    if not DB_PATH.exists(): build_warehouse()
    return sqlite3.connect(DB_PATH)

def roll_up():
    # Aggregate encounter metrics from admission type to a compact admission summary.
    with _conn() as c:
        return pd.read_sql_query('''SELECT a.admission_type_id, COUNT(*) encounters,
          ROUND(AVG(f.time_in_hospital),2) avg_length_of_stay,
          ROUND(AVG(CASE WHEN f.readmitted <> 'NO' THEN 1.0 ELSE 0 END)*100,2) readmission_pct
          FROM Fact_Encounter f JOIN Dim_Admission a USING(dim_admission_key)
          GROUP BY a.admission_type_id ORDER BY encounters DESC''', c)

def drill_down(admission_type_id=None):
    sql = '''SELECT a.admission_type_id, a.admission_source_id, d.discharge_disposition_id,
      COUNT(*) encounters, ROUND(AVG(f.time_in_hospital),2) avg_length_of_stay
      FROM Fact_Encounter f JOIN Dim_Admission a USING(dim_admission_key)
      JOIN Dim_Discharge d USING(dim_discharge_key)'''
    params=()
    if admission_type_id is not None:
        sql += ' WHERE a.admission_type_id=?'; params=(int(admission_type_id),)
    sql += ' GROUP BY 1,2,3 ORDER BY encounters DESC'
    with _conn() as c: return pd.read_sql_query(sql,c,params=params)

def slice_readmission(label='>30'):
    with _conn() as c:
        return pd.read_sql_query('''SELECT readmitted, COUNT(*) encounters,
          ROUND(AVG(time_in_hospital),2) avg_length_of_stay FROM Fact_Encounter
          WHERE readmitted=? GROUP BY readmitted''',c,params=(label,))

def dice(admission_type_id=1, readmitted='>30'):
    with _conn() as c:
        return pd.read_sql_query('''SELECT a.admission_type_id, f.readmitted, COUNT(*) encounters,
          ROUND(AVG(f.num_medications),2) avg_medications FROM Fact_Encounter f
          JOIN Dim_Admission a USING(dim_admission_key)
          WHERE a.admission_type_id=? AND f.readmitted=? GROUP BY 1,2''',c,params=(int(admission_type_id),readmitted))

def pivot():
    with _conn() as c:
        df=pd.read_sql_query('''SELECT a.admission_type_id, f.readmitted, COUNT(*) encounters
          FROM Fact_Encounter f JOIN Dim_Admission a USING(dim_admission_key)
          GROUP BY 1,2''',c)
    return df.pivot(index='admission_type_id',columns='readmitted',values='encounters').fillna(0).reset_index()

def run_olap():
    outputs={'olap_rollup.csv':roll_up(),'olap_drilldown.csv':drill_down(),
             'olap_slice.csv':slice_readmission(), 'olap_dice.csv':dice(), 'olap_pivot.csv':pivot()}
    for name,df in outputs.items(): df.to_csv(TABLES/name,index=False)
    return {name:len(df) for name,df in outputs.items()}

if __name__ == '__main__': print(run_olap())
