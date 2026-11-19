from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "diabetic_data.csv"
CLEAN = ROOT / "data" / "processed" / "diabetic_data_cleaned.csv"
OUT = ROOT / "outputs"
TABLES = OUT / "tables"
FIGURES = OUT / "figures"

st.set_page_config(
    page_title="MediScope | Diabetes Analytics",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A clean, bright dashboard theme with a restrained accent palette.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17233b; --muted:#718096; --line:#e8edf5; --panel:#ffffff; --bg:#f5f7fb; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--bg); }
.block-container { padding-top:1.8rem; padding-bottom:2.5rem; max-width:1500px; }
[data-testid="stSidebar"] { background:#111c34; border-right:1px solid #263653; }
[data-testid="stSidebar"] * { color:#edf3ff !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:9px 12px; border-radius:10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#243653; }
.hero { background:linear-gradient(115deg,#172b4d 0%,#264d73 55%,#347b89 100%); padding:27px 30px; border-radius:20px; color:white; margin-bottom:22px; box-shadow:0 12px 30px rgba(26,49,81,.12); }
.hero h1 { color:white; font-family:'Manrope',sans-serif; font-size:31px; margin:0 0 5px 0; font-weight:800; }
.hero p { color:#d9e8f4; margin:0; font-size:14px; }
.eyebrow { color:#b8d8e9; text-transform:uppercase; letter-spacing:1.7px; font-size:10px; font-weight:800; margin-bottom:7px; }
.section-title { font-family:'Manrope',sans-serif; color:var(--ink); font-weight:800; font-size:19px; margin:15px 0 4px 0; }
.section-sub { color:var(--muted); font-size:12px; margin-bottom:12px; }
.metric-card { background:white; border:1px solid var(--line); border-radius:16px; padding:17px 18px; box-shadow:0 3px 12px rgba(30,50,80,.035); min-height:112px; }
.metric-label { color:#718096; font-size:12px; font-weight:600; margin-bottom:9px; }
.metric-value { color:#17233b; font-family:'Manrope',sans-serif; font-size:27px; font-weight:800; line-height:1.1; }
.metric-note { color:#94a3b8; font-size:11px; margin-top:7px; }
.panel { background:white; border:1px solid var(--line); border-radius:16px; padding:16px 18px; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.stAlert { border-radius:12px; }
hr { border-color:var(--line); }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

PALETTE = ["#4776E6", "#19B6A4", "#F4A340", "#9B72CF", "#E56B83", "#54A6D8", "#7EBD75"]
READMISSION_COLORS = {"NO": "#19B6A4", ">30": "#F4A340", "<30": "#E56B83"}

@st.cache_data(show_spinner="Loading encounter data...")
def load_data():
    path = CLEAN if CLEAN.exists() else RAW
    data = pd.read_csv(path, low_memory=False)
    return data.replace("?", "Unknown")

df = load_data()


def section(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def metric(label, value, note=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def chart(fig, height=340):
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=12, r=12, t=48, b=12),
        font=dict(family="DM Sans", color="#526079", size=11),
        title=dict(font=dict(family="Manrope", size=15, color="#17233b"), x=0.02),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, linecolor="#e8edf5", zeroline=False)
    fig.update_yaxes(gridcolor="#edf1f7", zeroline=False)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


st.sidebar.markdown("<div style='font-size:27px;font-weight:800;font-family:Manrope;color:white'>✚ MediScope</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:11px;color:#a9bdd7;margin:2px 0 20px'>DIABETES PATIENT ANALYTICS</div>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "WORKSPACE",
    ["Executive Overview", "Patient Trends", "Clinical & Medication", "Readmission Insights", "Models & Data Mining", "Data Warehouse & OLAP", "Data Quality"],
    label_visibility="visible",
)
st.sidebar.divider()
st.sidebar.markdown("<div style='font-size:11px;color:#a9bdd7;line-height:1.6'>MDM · DATA ANALYTICS PROJECT<br>Academic use only · Not for clinical decisions</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><div class="eyebrow">HEALTHCARE ANALYTICS WORKSPACE</div>'
    '<h1>Diabetes Patient Intelligence</h1>'
    '<p>Explore hospital encounters, readmission patterns, clinical indicators and data-mining results.</p></div>',
    unsafe_allow_html=True,
)

if page == "Executive Overview":
    total = len(df)
    patients = df["patient_nbr"].nunique() if "patient_nbr" in df else 0
    avg_stay = df["time_in_hospital"].mean() if "time_in_hospital" in df else 0
    early = (df["readmitted"] == "<30").mean() * 100 if "readmitted" in df else 0

    cols = st.columns(4)
    with cols[0]:
        metric("TOTAL ENCOUNTERS", f"{total:,}", "Hospital encounter records")
    with cols[1]:
        metric("UNIQUE PATIENTS", f"{patients:,}", "Distinct patient identifiers")
    with cols[2]:
        metric("AVERAGE LENGTH OF STAY", f"{avg_stay:.1f} days", "Across recorded encounters")
    with cols[3]:
        metric("READMITTED UNDER 30 DAYS", f"{early:.1f}%", "Share of all encounters")

    section("Encounter snapshot", "A quick view of readmission mix and patient age distribution.")

    left, right = st.columns([1, 1.25], gap="large")

    with left:
        if "readmitted" in df:
            counts = df["readmitted"].value_counts().reindex(["NO", ">30", "<30"]).fillna(0).rename_axis("Status").reset_index(name="Encounters")
            fig = px.pie(counts, names="Status", values="Encounters", hole=.66,
                         color="Status", color_discrete_map=READMISSION_COLORS)
            fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="white", width=3)))
            fig.update_layout(title="Readmission distribution", showlegend=False)
            chart(fig, 350)

    with right:
        if "age" in df:
            order = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
            age = df["age"].value_counts().reindex(order).dropna().rename_axis("Age band").reset_index(name="Encounters")
            fig = px.bar(age, x="Age band", y="Encounters", color="Encounters", color_continuous_scale=["#c8dcf7", "#4776E6"])
            fig.update_layout(title="Encounters by age band", coloraxis_showscale=False)
            chart(fig, 350)

    section("Data preview", "First 10 rows from the active dataset.")
    st.dataframe(df.head(10), width="stretch", height=300)

elif page == "Patient Trends":
    section("Patient & encounter trends", "Understand the patient mix and duration of hospital stays.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        if "time_in_hospital" in df:
            fig = px.histogram(df, x="time_in_hospital", nbins=14, color_discrete_sequence=["#4776E6"])
            fig.update_layout(title="Length of stay distribution", xaxis_title="Days in hospital", yaxis_title="Encounters")
            chart(fig)
    with c2:
        if "age" in df:
            age = df["age"].value_counts().rename_axis("Age band").reset_index(name="Encounters")
            fig = px.bar(age, x="Age band", y="Encounters", color="Age band", color_discrete_sequence=PALETTE)
            fig.update_layout(title="Encounter volume by age", showlegend=False)
            chart(fig)
    if "admission_type_id" in df and "readmitted" in df:
        cross = pd.crosstab(df["admission_type_id"], df["readmitted"]).reindex(columns=["NO", ">30", "<30"], fill_value=0).reset_index()
        fig = px.bar(cross, x="admission_type_id", y=[x for x in ["NO", ">30", "<30"] if x in cross],
                     barmode="group", color_discrete_map=READMISSION_COLORS)
        fig.update_layout(title="Readmission outcomes by admission type", xaxis_title="Admission type ID", yaxis_title="Encounters")
        chart(fig, 380)

elif page == "Clinical & Medication":
    section("Clinical & medication patterns", "Compare recorded medication indicators and glucose-related measures.")
    meds = [c for c in ["metformin", "insulin", "glipizide", "glyburide", "pioglitazone", "rosiglitazone", "diabetesMed"] if c in df]
    if meds:
        selected = st.selectbox("Select a medication indicator", meds)
        plot_df = df[[selected] + (["readmitted"] if "readmitted" in df else [])].copy()
        counts = plot_df.groupby([selected] + (["readmitted"] if "readmitted" in plot_df else []), dropna=False).size().reset_index(name="Encounters")
        fig = px.bar(counts, x=selected, y="Encounters", color="readmitted" if "readmitted" in counts else selected,
                     barmode="group", color_discrete_map=READMISSION_COLORS if "readmitted" in counts else None,
                     color_discrete_sequence=PALETTE)
        fig.update_layout(title=f"{selected}: encounter distribution", xaxis_title=selected)
        chart(fig)
    c1, c2 = st.columns(2, gap="large")
    for col, container in zip(["A1Cresult", "max_glu_serum"], [c1, c2]):
        if col in df:
            counts = df[col].value_counts(dropna=False).rename_axis("Result").reset_index(name="Encounters")
            fig = px.bar(counts, x="Result", y="Encounters", color="Result", color_discrete_sequence=PALETTE)
            fig.update_layout(title=f"{col} distribution", showlegend=False)
            with container:
                chart(fig)

elif page == "Readmission Insights":
    section("Readmission insights", "Filter encounter outcomes and compare readmission patterns.")
    statuses = [x for x in ["NO", ">30", "<30"] if "readmitted" in df and x in set(df["readmitted"].astype(str))]
    selected_status = st.multiselect("Readmission categories", statuses, default=statuses)
    view = df[df["readmitted"].isin(selected_status)] if "readmitted" in df else df
    a, b = st.columns(2, gap="large")
    with a:
        if "age" in view and "readmitted" in view:
            cross = pd.crosstab(view["age"], view["readmitted"], normalize="index").reindex(columns=["NO", ">30", "<30"], fill_value=0).reset_index()
            fig = px.bar(cross, x="age", y=[x for x in ["NO", ">30", "<30"] if x in cross], barmode="stack",
                         color_discrete_map=READMISSION_COLORS)
            fig.update_layout(title="Readmission mix by age band", yaxis_tickformat=".0%", yaxis_title="Share of encounters")
            chart(fig)
    with b:
        if "time_in_hospital" in view and "readmitted" in view:
            fig = px.box(view, x="readmitted", y="time_in_hospital", color="readmitted",
                         category_orders={"readmitted": ["NO", ">30", "<30"]}, color_discrete_map=READMISSION_COLORS)
            fig.update_layout(title="Length of stay by readmission outcome", xaxis_title="Readmission status", yaxis_title="Days")
            chart(fig)
    display_cols = [c for c in ["readmitted", "age", "time_in_hospital", "race", "gender", "diabetesMed"] if c in view]
    st.dataframe(view[display_cols].head(100), width="stretch", height=330)

elif page == "Models & Data Mining":
    section("Models & data mining", "Review the generated model metrics and association-mining outputs.")
    metrics_path = TABLES / "decision_tree_comparison.csv"
    if metrics_path.exists():
        models = pd.read_csv(metrics_path)
        if {"algorithm", "accuracy"}.issubset(models.columns):
            fig = px.bar(models.sort_values("accuracy", ascending=True), x="accuracy", y="algorithm", orientation="h",
                         text=models.sort_values("accuracy", ascending=True)["accuracy"].map(lambda x: f"{x:.1%}"),
                         color="accuracy", color_continuous_scale=["#f5c36b", "#19b6a4", "#4776e6"])
            fig.update_layout(title="Decision-tree accuracy comparison", xaxis_tickformat=".0%", coloraxis_showscale=False, yaxis_title="")
            chart(fig, 300)
    reg_path = TABLES / "regression_metrics.csv"
    if reg_path.exists():
        reg = pd.read_csv(reg_path)
        st.markdown("**Regression evaluation**")
        st.dataframe(reg, width="stretch")
    for filename, title in [
        ("decision_tree_comparison.csv", "Decision-tree comparison"),
        ("apriori_rules.csv", "Apriori association rules"),
        ("fp_growth_itemsets.csv", "FP-Growth frequent itemsets"),
        ("multilevel_itemsets.csv", "Multilevel association itemsets"),
    ]:
        path = TABLES / filename
        if path.exists():
            with st.expander(title, expanded=(filename == "apriori_rules.csv")):
                st.dataframe(pd.read_csv(path).head(100), width="stretch")
    heatmap = FIGURES / "correlation_heatmap.png"
    if heatmap.exists():
        section("Correlation overview")
        st.image(str(heatmap), width="stretch")

elif page == "Data Warehouse & OLAP":
    section("Data warehouse & dimensional model", "Explore the SQLite star schema built from the encounter-level source data.")
    db_path = ROOT / "data" / "warehouse" / "mediscope_warehouse.db"
    if not db_path.exists():
        st.warning("Warehouse not built yet. Run `py -3.11 -m src.run_all` from the project folder.")
    else:
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", conn)
            st.dataframe(tables, width="stretch")
            fact_count = pd.read_sql_query("SELECT COUNT(*) n FROM Fact_Encounter", conn).iloc[0,0]
        c1,c2 = st.columns(2)
        with c1: metric("WAREHOUSE FACT ROWS", f"{fact_count:,}", "One row per hospital encounter")
        with c2: metric("DIMENSION TABLES", str(sum(t.startswith("Dim_") for t in tables.name)), "Descriptive lookup dimensions")
        section("OLAP operations", "Choose an operation to explore multidimensional summaries.")
        operation = st.selectbox("OLAP operation", ["Roll-up", "Drill-down", "Slice", "Dice", "Pivot"])
        from src import olap
        if operation == "Roll-up": result = olap.roll_up()
        elif operation == "Drill-down":
            admission = st.selectbox("Admission type ID (optional filter)", ["All"] + sorted(df.admission_type_id.dropna().unique().tolist()))
            result = olap.drill_down(None if admission == "All" else admission)
        elif operation == "Slice":
            status = st.selectbox("Readmission status", ["NO", ">30", "<30"])
            result = olap.slice_readmission(status)
        elif operation == "Dice":
            admission = st.selectbox("Admission type", sorted(df.admission_type_id.dropna().unique().tolist()))
            status = st.selectbox("Readmission status filter", ["NO", ">30", "<30"])
            result = olap.dice(admission,status)
        else: result = olap.pivot()
        st.dataframe(result, width="stretch")
        st.download_button("Download OLAP result CSV", result.to_csv(index=False), file_name=f"mediscope_{operation.lower().replace('-', '_')}.csv", mime="text/csv")
        st.caption("No Dim_Date is modelled because the supplied UCI file does not contain an encounter date field.")

elif page == "Data Quality":
    section("Data quality & methodology", "Inspect missingness and understand how the analysis was prepared.")
    missing_path = TABLES / "missing_value_report.csv"
    if missing_path.exists():
        miss = pd.read_csv(missing_path).sort_values("missing_pct", ascending=False).head(20)
        if {"column", "missing_pct"}.issubset(miss.columns):
            fig = px.bar(miss.sort_values("missing_pct"), x="missing_pct", y="column", orientation="h",
                         color="missing_pct", color_continuous_scale=["#f4c36e", "#e56b83"])
            fig.update_layout(title="Top fields by missing-value percentage", xaxis_title="Missing values (%)", yaxis_title="", coloraxis_showscale=False)
            chart(fig, 480)
        st.dataframe(miss, width="stretch")
    else:
        missing = df.isna().sum().sort_values(ascending=False).head(20).rename_axis("Column").reset_index(name="Missing values")
        st.dataframe(missing, width="stretch")
    with st.expander("Methodology notes", expanded=True):
        st.markdown("""
        - One row represents a hospital encounter; a patient may appear in multiple rows.
        - Patient and encounter identifiers should not be used as predictive features.
        - The `?` placeholder is represented as `Unknown` in this dashboard.
        - High-missingness fields require careful handling before modelling.
        - Patient-group splitting helps reduce leakage between train and test sets.
        - Readmission associations are observational and do not establish causation.
        - This academic project is not a clinical decision-support system.
        """)

st.markdown("<hr><div style='text-align:center;color:#94a3b8;font-size:11px;padding:8px'>MediScope · MDM Data Analytics Project · Academic use only</div>", unsafe_allow_html=True)
