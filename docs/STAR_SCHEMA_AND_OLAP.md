# MediScope warehouse and OLAP notes

## Fact grain
One row in `Fact_Encounter` represents one hospital encounter in the source dataset. It contains the source encounter ID, encounter-level numeric measures, readmission label and foreign keys to descriptive dimensions.

## Star schema

```text
                    Dim_Patient
                         |
Dim_Admission --- Fact_Encounter --- Dim_Discharge
                         |
                   Dim_Diagnosis
                         |
                  Dim_Medication
```

The schema is a practical star-style design for the fields available in this dataset. Dimension rows are generated from distinct combinations of their natural attributes and assigned integer surrogate keys. The ETL rebuilds the warehouse from the cleaned extract so the output is reproducible.

## Why there is no Dim_Date
The supplied data has no admission or encounter date field. A date dimension without a source date would be fabricated and misleading. Add it only when a suitable date-bearing source is available.

## OLAP mapping

| OLAP operation | MediScope implementation | Example question |
|---|---|---|
| Roll-up | Aggregate by admission type | How many encounters and what average stay per admission type? |
| Drill-down | Admission type → source → discharge | What detail sits under an admission category? |
| Slice | Filter one readmission value | What do encounters labelled `>30` look like? |
| Dice | Filter admission type and readmission value | What is the subset for admission type 1 and `>30`? |
| Pivot | Readmission labels become columns | Compare readmission mix across admission types |

## Important interpretation note
The dimensions describe available source attributes, not verified clinical entities. The patient identifier is a de-identified source key. No claim is made that the data represents current hospital operations or that patterns are causal.
