"""Executive Streamlit dashboard with robust runtime behavior."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is importable when Streamlit runs from dashboard/app.py.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import Settings  # noqa: E402
from src.data.sqlite_manager import SQLiteManager  # noqa: E402
from src.utils.observability import get_structured_logger, new_trace_id, timed_stage  # noqa: E402

PAGE_OPTIONS = [
    "Overview",
    "Upload",
    "Data",
    "EDA",
    "Visualizations",
    "Database",
    "Settings",
]

st.set_page_config(
    page_title="Data Senior Analytics",
    page_icon="DA",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_LOGGER = get_structured_logger("dashboard_app")


def apply_executive_style() -> None:
    st.markdown(
        """
        <style>
            html, body, [class*="css"] {
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            }
            .stApp {
                background: linear-gradient(180deg, #f5f7fa 0%, #eef2f7 100%);
            }
            .main .block-container {
                max-width: 1240px;
                padding-top: 1.2rem;
                padding-bottom: 2rem;
            }
            .hero {
                padding: 1rem 1.2rem;
                border: 1px solid #d8dee8;
                border-radius: 12px;
                background: #ffffff;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
                margin-bottom: 0.8rem;
            }
            .hero-title {
                margin: 0;
                color: #0f172a;
                font-size: 2rem;
                font-weight: 750;
                letter-spacing: -0.02em;
            }
            .hero-subtitle {
                margin: 0.35rem 0 0 0;
                color: #475569;
                font-size: 0.95rem;
            }
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid #d8dee8;
                border-radius: 12px;
                padding: 0.45rem 0.7rem;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            }
            div[role="radiogroup"] > label {
                border: 1px solid #d8dee8;
                border-radius: 10px;
                padding: 0.18rem 0.55rem;
                background: #ffffff;
                margin-right: 0.2rem;
            }
            .exec-pill {
                display: inline-block;
                padding: 0.2rem 0.55rem;
                border-radius: 999px;
                border: 1px solid #cbd5e1;
                color: #0f172a;
                font-size: 0.78rem;
                background: #f8fafc;
                margin-bottom: 0.4rem;
            }
            .exec-card-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.35rem;
            }
            .exec-chip-row {
                margin-top: 0.5rem;
                margin-bottom: 0.25rem;
            }
            .exec-chip {
                display: inline-block;
                margin-right: 0.35rem;
                margin-bottom: 0.25rem;
                padding: 0.18rem 0.5rem;
                border: 1px solid #d1d9e6;
                border-radius: 999px;
                background: #f8fafc;
                color: #334155;
                font-size: 0.75rem;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_db() -> SQLiteManager:
    return SQLiteManager()


@st.cache_data
def load_default_demo_data() -> pd.DataFrame:
    demo_path = Settings.SAMPLE_DATA_DIR / "default_demo.csv"
    if demo_path.exists():
        return pd.read_csv(demo_path)
    return pd.DataFrame()


@st.cache_data
def get_build_id() -> str:
    env_build = os.getenv("STREAMLIT_GIT_SHA") or os.getenv("GITHUB_SHA")
    if env_build:
        return env_build[:8]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:  # noqa: BLE001
        pass
    return "unknown"


def ensure_session_defaults() -> None:
    if "data" not in st.session_state:
        st.session_state.data = None
    if "data_name" not in st.session_state:
        st.session_state.data_name = None
    if "data_source" not in st.session_state:
        st.session_state.data_source = None
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Overview"

    if st.session_state.data is None:
        demo_df = load_default_demo_data()
        if not demo_df.empty:
            st.session_state.data = demo_df
            st.session_state.data_name = "default_demo.csv"
            st.session_state.data_source = "sample_auto"


def render_header(df: pd.DataFrame | None) -> None:
    st.markdown(
        """
        <div class="hero">
            <h1 class="hero-title">Data Senior Analytics</h1>
            <p class="hero-subtitle">Executive dashboard for diagnostics, exploration, and decision support.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Environment", "Executive")
    with c2:
        st.metric("Build", get_build_id())
    with c3:
        if df is not None and not df.empty:
            st.metric("Active dataset", st.session_state.data_name)
        else:
            st.metric("Active dataset", "No data")

    st.markdown(
        """
        <div class="exec-chip-row">
            <span class="exec-chip">Business-ready analytics</span>
            <span class="exec-chip">Data governance by design</span>
            <span class="exec-chip">Executive decision support</span>
            <span class="exec-chip">Production-ready Streamlit</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home(df: pd.DataFrame | None, db: SQLiteManager) -> None:
    st.subheader("Executive Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Python", "3.11")
    with c2:
        st.metric("Framework", "Streamlit")
    with c3:
        st.metric("Source", "Kaggle")
    with c4:
        st.metric("SQLite tables", len(db.list_tables()))

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Direction</span>', unsafe_allow_html=True)
            st.markdown('<div class="exec-card-title">Objective</div>', unsafe_allow_html=True)
            st.write("Turn tabular data into actionable insights for fast, reliable decisions.")
            st.markdown('<div class="exec-card-title">Value</div>', unsafe_allow_html=True)
            st.write("End-to-end analytics workflow with senior engineering standards.")

    with right:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Data context</span>', unsafe_allow_html=True)
            st.markdown('<div class="exec-card-title">Data Status</div>', unsafe_allow_html=True)
            if df is not None and not df.empty:
                st.write(f"Dataset: **{st.session_state.data_name}**")
                st.write(f"Rows: **{df.shape[0]:,}**")
                st.write(f"Columns: **{df.shape[1]}**")
                st.write(f"Source: **{st.session_state.data_source}**")
            else:
                st.info("No dataset loaded.")

    s1, s2, s3 = st.columns(3)
    if df is not None and not df.empty:
        null_rate = (df.isna().sum().sum() / max(1, (df.shape[0] * df.shape[1]))) * 100
        dup_rate = (df.duplicated().sum() / max(1, df.shape[0])) * 100
        numeric_cols = df.select_dtypes(include="number").shape[1]
        insight_msg = f"Dataset ready for exploration with {numeric_cols} numeric columns."
        risk_msg = f"Missing: {null_rate:.2f}% | Duplicates: {dup_rate:.2f}%."
        action_msg = "Run EDA first, then persist curated outputs in SQLite."
    else:
        insight_msg = "No active dataset to generate executive insights."
        risk_msg = "Risk cannot be estimated without loaded data."
        action_msg = "Start with the Upload page and validate minimum data quality."

    with s1:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Insight</span>', unsafe_allow_html=True)
            st.write(insight_msg)
    with s2:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Risk</span>', unsafe_allow_html=True)
            st.write(risk_msg)
    with s3:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Action</span>', unsafe_allow_html=True)
            st.write(action_msg)

    st.markdown("### Professional Highlights")
    d1, d2 = st.columns(2)
    with d1:
        with st.container(border=True):
            st.markdown("#### For Recruiters")
            st.write("- End-to-end delivery: ingestion, EDA, visualization, and persistence.")
            st.write("- Executive communication focused on business value and decisions.")
            st.write("- Project quality with reproducibility and governance.")
    with d2:
        with st.container(border=True):
            st.markdown("#### For Technical Leads")
            st.write("- Modular architecture with clear responsibilities.")
            st.write("- Active quality gates: lint, tests, and deployment preflight.")
            st.write("- Explicit data governance with Kaggle provenance.")

    st.markdown("### Analytics Maturity")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.caption("Data Reliability")
        st.progress(88)
    with m2:
        st.caption("Production Readiness")
        st.progress(90)
    with m3:
        st.caption("Executive Clarity")
        st.progress(92)

    st.markdown("### Technical Seniority Signals")
    st.write(
        "- Layered architecture with clear responsibilities (`dashboard/`, `src/`, `config/`)."
    )
    st.write("- Locally executable pipeline via `make` and preflight validations.")
    st.write("- Quality standards with automated tests, coverage, and data contracts.")
    st.write("- Decision-oriented dashboard with KPI, trend, and executive narrative.")

    if df is not None and not df.empty and {"categoria", "valor_total"}.issubset(df.columns):
        category_revenue = (
            df.groupby("categoria", dropna=False)["valor_total"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_n = len(category_revenue)
        fig = px.bar(
            category_revenue,
            x="valor_total",
            y="categoria",
            orientation="h",
            title=f"Top {top_n} Categories by Revenue",
            labels={"categoria": "product_category", "valor_total": "revenue"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)


def render_upload(db: SQLiteManager) -> None:
    st.subheader("Data Upload")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    if uploaded is None:
        st.info("Upload a file to replace the default demo dataset.")
        return

    try:
        if uploaded.name.lower().endswith(".csv"):
            # Common fallback chain for CSV files produced by spreadsheet tools.
            for encoding in ("utf-8", "utf-8-sig", "latin-1"):
                uploaded.seek(0)
                try:
                    df = pd.read_csv(uploaded, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                uploaded.seek(0)
                df = pd.read_csv(uploaded)
        else:
            uploaded.seek(0)
            df = pd.read_excel(uploaded)
    except Exception as exc:  # noqa: BLE001
        st.error("Failed to read the uploaded file. Please verify format and encoding.")
        st.exception(exc)
        return

    if df.empty:
        st.warning("The uploaded file contains no rows.")
        return

    st.session_state.data = df
    st.session_state.data_name = uploaded.name
    st.session_state.data_source = "upload"

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Rows", f"{df.shape[0]:,}")
    with k2:
        st.metric("Columns", df.shape[1])
    with k3:
        st.metric("Memory", f"{df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")

    st.success(f"File loaded successfully: {uploaded.name}")
    st.caption("Preview (first 50 rows)")
    st.table(df.head(50))

    table_name = st.text_input(
        "SQLite table name",
        value=uploaded.name.replace(".", "_"),
        key="upload_table_name",
    )
    if st.button("Save to SQLite", key="save_sqlite_button", use_container_width=True):
        ok = db.df_to_sql(df, table_name)
        if ok:
            st.success(f"Table saved: {table_name}")
        else:
            st.error("Failed to save table to SQLite.")


def render_data_preview(df: pd.DataFrame | None) -> None:
    st.subheader("Data Preview")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    tab1, tab2 = st.tabs(["Sample", "Column Profile"])

    with tab1:
        st.caption("Preview (first 200 rows)")
        st.table(df.head(200))

    with tab2:
        info = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Missing": df.isna().sum().values,
                "Unique": [df[c].nunique(dropna=True) for c in df.columns],
            }
        )
        st.table(info)


def render_eda(df: pd.DataFrame | None) -> None:
    st.subheader("Exploratory Analysis")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    numeric = df.select_dtypes(include="number")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows", f"{len(df):,}")
    with c2:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with c3:
        st.metric("Duplicate rows", int(df.duplicated().sum()))

    if numeric.empty:
        st.info("No numeric columns available for descriptive statistics.")
        return

    tab_stats, tab_corr = st.tabs(["Statistics", "Correlation"])

    with tab_stats:
        st.table(numeric.describe().T)

    with tab_corr:
        if numeric.shape[1] > 1:
            corr = numeric.corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("At least 2 numeric columns are required.")


def render_charts(df: pd.DataFrame | None) -> None:
    st.subheader("Visualizations")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if numeric_cols:
        col = st.selectbox("Numeric variable", numeric_cols, key="chart_numeric_variable")
        fig = px.histogram(df, x=col, nbins=30, title=f"Distribution: {col}")
        st.plotly_chart(fig, use_container_width=True)

    if cat_cols and numeric_cols:
        left, right = st.columns(2)
        with left:
            cat = st.selectbox("Category", cat_cols, key="chart_category")
        with right:
            val = st.selectbox(
                "Metric",
                numeric_cols,
                index=min(1, len(numeric_cols) - 1),
                key="chart_metric",
            )
        grouped = (
            df.groupby(cat, dropna=False)[val]
            .mean()
            .reset_index()
            .sort_values(val, ascending=False)
        )
        fig = px.bar(grouped.head(15), x=cat, y=val, title=f"Average {val} by {cat}")
        st.plotly_chart(fig, use_container_width=True)


def render_database(db: SQLiteManager) -> None:
    st.subheader("SQLite Database")
    tables = db.list_tables()
    if not tables:
        st.info("No tables found in SQLite.")
        return

    table = st.selectbox("Table", tables, key="database_table")
    count = db.fetch_scalar(f"SELECT COUNT(*) FROM [{table}]") or 0
    st.metric("Rows in table", int(count))

    preview = db.sql_to_df(f"SELECT * FROM [{table}] LIMIT 500")
    st.caption("Table preview (up to 500 rows)")
    st.table(preview)


def render_settings(df: pd.DataFrame | None) -> None:
    st.subheader("Settings and Runtime")
    st.json(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
            "sqlite_path": str(Settings.SQLITE_PATH),
        }
    )


def main() -> None:
    trace_id = new_trace_id()
    ensure_session_defaults()
    apply_executive_style()
    db = get_db()
    df = st.session_state.data
    APP_LOGGER.info(
        "app_start",
        extra={
            "trace_id": trace_id,
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
        },
    )

    render_header(df)
    page = st.radio(
        "Navigation",
        PAGE_OPTIONS,
        horizontal=True,
        key="selected_page",
        label_visibility="collapsed",
    )

    with st.sidebar:
        st.markdown("## Context")
        st.caption(f"Build: `{get_build_id()}`")
        st.caption(f"Page: **{page}**")
        if df is not None and not df.empty:
            st.caption(f"Dataset: **{st.session_state.data_name}**")
            st.caption(f"Rows: {df.shape[0]:,}")
            st.caption(f"Columns: {df.shape[1]}")
            if st.session_state.data_source == "sample_auto":
                st.info("Default demo dataset loaded automatically.")

        st.link_button(
            "PT-BR version",
            "https://github.com/samuelmaia-data-analyst/data-senior-analytics/blob/main/README.md",
            use_container_width=True,
        )

        if st.button("Reset session", use_container_width=True):
            for key in ("data", "data_name", "data_source"):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    page_handlers = {
        "Overview": lambda: render_home(df, db),
        "Upload": lambda: render_upload(db),
        "Data": lambda: render_data_preview(df),
        "EDA": lambda: render_eda(df),
        "Visualizations": lambda: render_charts(df),
        "Database": lambda: render_database(db),
        "Settings": lambda: render_settings(df),
    }

    try:
        with timed_stage(f"render_page:{page}") as timer:
            page_handlers[page]()
        APP_LOGGER.info(
            "page_rendered",
            extra={"trace_id": trace_id, "page": page, "elapsed_ms": round(timer.elapsed_ms, 2)},
        )
    except Exception as exc:  # noqa: BLE001
        APP_LOGGER.error(
            "page_render_failed", extra={"trace_id": trace_id, "page": page, "error": str(exc)}
        )
        st.error("Failed to render this page. The app is still available.")
        st.exception(exc)


if __name__ == "__main__":
    main()
