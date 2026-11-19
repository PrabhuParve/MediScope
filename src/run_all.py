from src.prepare_data import prepare
from src.eda import run_eda
from src.decision_trees import run_trees
from src.association_rules import run_association
from src.regression import run_regression
from src.warehouse import build_warehouse
from src.olap import run_olap

def main():
    steps=[('Data cleaning and validation',prepare),('Exploratory analysis',run_eda),
           ('Decision-tree comparison',run_trees),('Association-rule mining (Apriori + FP-Growth)',run_association),
           ('Correlation and regression',run_regression),('Star-schema warehouse ETL',build_warehouse),
           ('OLAP operations',run_olap)]
    for i,(label,func) in enumerate(steps,1):
        print(f'\\n[{i}/{len(steps)}] {label}')
        print(func())
    print('\\nAll tasks completed. Review outputs/, models/, and data/warehouse/.')

if __name__=='__main__': main()
