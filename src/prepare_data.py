"""Reproducible cleaning and validation for the UCI diabetes encounters data."""
import pandas as pd
import numpy as np
from src.common import load_raw, CLEAN_PATH, TABLES

def prepare():
    df=load_raw().copy()
    df.columns=[c.strip() for c in df.columns]
    for col in df.select_dtypes(include='object'):
        df[col]=df[col].astype('string').str.strip().replace('',pd.NA)
    before=len(df); duplicate_count=int(df.duplicated().sum()); df=df.drop_duplicates().copy()
    missing_before=df.isna().sum().rename('missing_count').to_frame()
    missing_before['missing_pct']=(missing_before.missing_count/len(df)*100).round(2)
    # Exclude fields with extreme missingness from the analytical cleaned extract;
    # retain the original raw file unchanged and record the exclusion explicitly.
    excluded=[c for c in ['weight','payer_code','medical_specialty'] if c in df.columns]
    df=df.drop(columns=excluded)
    # IDs remain for grouping/warehouse joins, but downstream predictive models must exclude them.
    for col in ['diag_1','diag_2','diag_3']:
        if col in df: df[col]=df[col].fillna('Unknown').astype(str)
    for col in df.select_dtypes(include=['object','string']).columns:
        df[col]=df[col].fillna('Unknown').astype(str)
    # Numeric source fields are not blindly imputed; missing counts are retained in report.
    df.to_csv(CLEAN_PATH,index=False)
    missing_before.rename_axis('column').reset_index().to_csv(TABLES/'missing_value_report.csv', index=False)
    quality=pd.DataFrame([
      {'check':'rows_before','value':before},{'check':'exact_duplicates_removed','value':duplicate_count},
      {'check':'rows_after','value':len(df)},{'check':'columns_after','value':len(df.columns)},
      {'check':'excluded_high_missingness_columns','value':', '.join(excluded)},
      {'check':'remaining_missing_cells','value':int(df.isna().sum().sum())},
      {'check':'duplicate_encounter_id_count','value':int(df.encounter_id.duplicated().sum()) if 'encounter_id' in df else 'N/A'}
    ])
    quality.to_csv(TABLES/'data_quality_report.csv',index=False)
    pd.DataFrame({'column':df.columns,'dtype':[str(x) for x in df.dtypes], 'unique_values':[df[c].nunique(dropna=False) for c in df.columns]}).to_csv(TABLES/'dataset_profile.csv',index=False)
    print(f'Prepared dataset: {df.shape}; removed {duplicate_count} exact duplicates; excluded {excluded}')
    return df

if __name__=='__main__': prepare()
