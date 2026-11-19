"""Apriori, FP-Growth, vertical TID format and two-level category association."""
from collections import defaultdict
from itertools import combinations
import pandas as pd
from src.common import load_clean, TABLES

TX_COLS = ["insulin", "metformin", "glipizide", "glyburide", "pioglitazone",
           "rosiglitazone", "diabetesMed", "A1Cresult", "max_glu_serum"]

def make_transactions(df, limit=6000):
    sample = df.sample(min(limit, len(df)), random_state=7)
    transactions = []
    for _, row in sample.iterrows():
        items = []
        for col in TX_COLS:
            if col in sample.columns:
                val = str(row[col])
                if val not in ("Unknown", "nan", "None", ""):
                    items.append(f"{col}={val}")
        # Add broad diagnosis category using first digit when available.
        diag = str(row.get("diag_1", "Unknown"))
        if diag and diag[0].isdigit():
            items.append("primary_diag_group=" + diag[0])
        transactions.append(sorted(set(items)))
    return transactions

def vertical_format(transactions):
    tid = defaultdict(set)
    for tid_id, transaction in enumerate(transactions):
        for item in transaction:
            tid[item].add(tid_id)
    return tid

def apriori(transactions, min_support=0.08, max_len=3):
    n = len(transactions)
    vertical = vertical_format(transactions)
    current = {frozenset([item]): ids for item, ids in vertical.items()
               if len(ids) / n >= min_support}
    frequent = dict(current)
    k = 2
    while current and k <= max_len:
        prev = list(current.keys())
        candidates = set()
        for i in range(len(prev)):
            for j in range(i + 1, len(prev)):
                union = prev[i] | prev[j]
                if len(union) == k:
                    candidates.add(union)
        next_level = {}
        for candidate in candidates:
            # Vertical TID intersection is the support-count calculation.
            ids = None
            for item in candidate:
                ids = vertical[item].copy() if ids is None else ids & vertical[item]
            if ids is not None and len(ids) / n >= min_support:
                next_level[candidate] = ids
        frequent.update(next_level)
        current = next_level
        k += 1
    return frequent

class FPNode:
    def __init__(self, item, parent):
        self.item, self.count, self.parent = item, 1, parent
        self.children = {}

def fp_growth(transactions, min_support=0.08):
    """Canonical recursive FP-Growth using conditional pattern bases and FP-trees.
    Returns frequent itemsets mapped to absolute support counts.
    """
    n = len(transactions)
    if not n: return {}
    min_count = max(1, int(min_support * n + 0.999999))
    counts = defaultdict(int)
    for trans in transactions:
        for item in set(trans): counts[item] += 1
    freq = {i:c for i,c in counts.items() if c >= min_count}
    if not freq: return {}
    root = FPNode(None, None)
    header = {i: [] for i in freq}
    for trans in transactions:
        ordered = sorted((i for i in set(trans) if i in freq), key=lambda x:(-freq[x],x))
        node = root
        for item in ordered:
            if item not in node.children:
                child = FPNode(item,node); node.children[item]=child; header[item].append(child)
            else: node.children[item].count += 1
            node=node.children[item]
    result = {}
    def mine(tree_header, suffix):
        # Least frequent item first; each conditional tree mines patterns ending in item.
        for item, nodes in sorted(tree_header.items(), key=lambda kv:(sum(x.count for x in kv[1]),kv[0])):
            support_count = sum(node.count for node in nodes)
            pattern = suffix | frozenset([item])
            result[pattern] = support_count
            conditional_paths=[]
            for node in nodes:
                path=[]; parent=node.parent
                while parent is not None and parent.item is not None:
                    path.append(parent.item); parent=parent.parent
                if path: conditional_paths.append((path,node.count))
            cond_counts=defaultdict(int)
            for path,count in conditional_paths:
                for x in path: cond_counts[x]+=count
            cond_freq={x:c for x,c in cond_counts.items() if c>=min_count}
            if not cond_freq: continue
            cond_root=FPNode(None,None); cond_header={x:[] for x in cond_freq}
            for path,count in conditional_paths:
                ordered=sorted((x for x in path if x in cond_freq),key=lambda x:(-cond_freq[x],x))
                cur=cond_root
                for x in ordered:
                    if x not in cur.children:
                        child=FPNode(x,cur); child.count=count; cur.children[x]=child; cond_header[x].append(child)
                    else: cur.children[x].count += count
                    cur=cur.children[x]
            mine(cond_header,pattern)
    mine(header,frozenset())
    return result

def rules_from_itemsets(itemsets, n_transactions, min_confidence=0.55):
    supports = {frozenset(k): v / n_transactions if isinstance(v, int) else v
                for k, v in itemsets.items()}
    rules = []
    for itemset, support in supports.items():
        if len(itemset) < 2:
            continue
        for size in range(1, len(itemset)):
            for left_tuple in combinations(itemset, size):
                left = frozenset(left_tuple)
                right = itemset - left
                if left in supports and supports[left] > 0:
                    confidence = support / supports[left]
                    if confidence >= min_confidence:
                        consequent_support = supports.get(right, 0)
                        lift = confidence / consequent_support if consequent_support else 0
                        rules.append({"antecedents": ", ".join(sorted(left)),
                                      "consequents": ", ".join(sorted(right)),
                                      "support": support, "confidence": confidence,
                                      "lift": lift})
    return pd.DataFrame(rules).drop_duplicates() if rules else pd.DataFrame(
        columns=["antecedents", "consequents", "support", "confidence", "lift"])

def run_association(sample_size=6000, min_support=0.08, min_confidence=0.55):
    df = load_clean()
    tx = make_transactions(df, sample_size)
    vertical = vertical_format(tx)
    apr = apriori(tx, min_support=min_support, max_len=3)
    apr_supports = {k: len(v) / len(tx) for k, v in apr.items()}
    apr_rules = rules_from_itemsets(apr_supports, len(tx), min_confidence)
    apr_rules = apr_rules.sort_values(["lift", "confidence"], ascending=False)
    apr_rules.to_csv(TABLES / "apriori_rules.csv", index=False)

    fp = fp_growth(tx, min_support=min_support)
    fp_df = pd.DataFrame([{"itemset": " | ".join(sorted(k)), "support": v}
                          for k, v in fp.items()])
    fp_df.sort_values("support", ascending=False).to_csv(TABLES / "fp_growth_itemsets.csv", index=False)

    # Multilevel association: group individual medications into medication categories.
    hierarchy = {
        "insulin": "Medication:Insulin",
        "metformin": "Medication:Biguanide",
        "glipizide": "Medication:Sulfonylurea",
        "glyburide": "Medication:Sulfonylurea",
        "pioglitazone": "Medication:Thiazolidinedione",
        "rosiglitazone": "Medication:Thiazolidinedione",
        "diabetesMed": "Medication:AnyDiabetesMedication"
    }
    multi = []
    for transaction in tx:
        mapped = set()
        for item in transaction:
            field = item.split("=", 1)[0]
            if field in hierarchy:
                mapped.add(hierarchy[field])
        multi.append(sorted(mapped))
    multi_itemsets = apriori(multi, min_support=min_support, max_len=2)
    multi_rows = [{"itemset": " | ".join(sorted(k)), "support": len(v)/len(multi)}
                  for k, v in multi_itemsets.items()]
    pd.DataFrame(multi_rows).to_csv(TABLES / "multilevel_itemsets.csv", index=False)

    print(f"Transactions: {len(tx)} | vertical items: {len(vertical)}")
    print(f"Apriori frequent itemsets: {len(apr)} | FP-growth itemsets: {len(fp)}")
    print("Top Apriori rules:")
    print(apr_rules.head(10).to_string(index=False))
    return apr_rules

if __name__ == "__main__":
    run_association()
