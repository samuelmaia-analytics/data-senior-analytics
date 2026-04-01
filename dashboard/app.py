"""Executive Streamlit dashboard with a curated analytics workflow."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is importable when Streamlit runs from dashboard/app.py.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import Settings  # noqa: E402
from dashboard.utils.analytics import (  # noqa: E402
    build_data_quality_summary,
    build_priority_actions,
    summarize_transformation_log,
)
from src.analysis.exploratory import ExploratoryAnalyzer  # noqa: E402
from src.data.sqlite_manager import SQLiteManager  # noqa: E402
from src.data.transformer import DataTransformer  # noqa: E402
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
def load_large_demo_data() -> pd.DataFrame:
    large_path = Settings.SAMPLE_DATA_DIR / "sample_large.csv"
    if large_path.exists():
        return pd.read_csv(large_path)
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


def prepare_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, Any]]]:
    """Run a lightweight curation pipeline and produce profiling metadata."""
    transformer = DataTransformer()
    curated_df = transformer.clean_column_names(df)
    curated_df = transformer.convert_dtypes(curated_df)
    curated_df = transformer.handle_missing_values(curated_df, strategy="auto")
    curated_df = transformer.remove_duplicates(curated_df)

    analyzer = ExploratoryAnalyzer()
    analysis = analyzer.analyze_dataframe(curated_df, df_name="active_dataset")
    transform_log = transformer.get_transformation_log()

    return curated_df, analysis, transform_log


def apply_dataset_to_session(df: pd.DataFrame, data_name: str, data_source: str) -> None:
    """Persist raw data, curated data, and metadata in the active session."""
    raw_df = df.copy()
    curated_df, analysis, transform_log = prepare_dataset(raw_df)
    quality_summary = build_data_quality_summary(curated_df)
    priority_actions = build_priority_actions(quality_summary)

    st.session_state.raw_data = raw_df
    st.session_state.data = curated_df
    st.session_state.data_name = data_name
    st.session_state.data_source = data_source
    st.session_state.analysis = analysis
    st.session_state.transform_log = transform_log
    st.session_state.quality_summary = quality_summary
    st.session_state.priority_actions = priority_actions


def clear_dataset_state() -> None:
    for key in (
        "raw_data",
        "data",
        "data_name",
        "data_source",
        "analysis",
        "transform_log",
        "quality_summary",
        "priority_actions",
    ):
        if key in st.session_state:
            del st.session_state[key]


def ensure_session_defaults() -> None:
    defaults = {
        "raw_data": None,
        "data": None,
        "data_name": None,
        "data_source": None,
        "analysis": None,
        "transform_log": [],
        "quality_summary": None,
        "priority_actions": [],
        "selected_page": "Overview",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.data is None:
        demo_df = load_default_demo_data()
        if not demo_df.empty:
            apply_dataset_to_session(demo_df, "default_demo.csv", "sample_auto")


def render_header(df: pd.DataFrame | None, quality_summary: dict[str, Any] | None) -> None:
    st.markdown(
        """
        <div class="hero">
            <h1 class="hero-title">Data Senior Analytics</h1>
            <p class="hero-subtitle">Executive dashboard for diagnostics, curation, exploration, and decision support.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
    with c1:
        st.metric("Environment", "Executive")
    with c2:
        st.metric("Build", get_build_id())
    with c3:
        if df is not None and not df.empty:
            st.metric("Active dataset", st.session_state.data_name)
        else:
            st.metric("Active dataset", "No data")
    with c4:
        score = quality_summary["quality_score"] if quality_summary else 0
        st.metric("Quality Score", f"{score:.0f}/100")

    st.markdown(
        """
        <div class="exec-chip-row">
            <span class="exec-chip">Business-ready analytics</span>
            <span class="exec-chip">Automated curation pipeline</span>
            <span class="exec-chip">Data governance by design</span>
            <span class="exec-chip">Executive decision support</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home(
    df: pd.DataFrame | None,
    db: SQLiteManager,
    quality_summary: dict[str, Any] | None,
    analysis: dict[str, Any] | None,
    priority_actions: list[str],
) -> None:
    st.subheader("Executive Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Python", "3.11")
    with c2:
        st.metric("Framework", "Streamlit")
    with c3:
        status = quality_summary["status"] if quality_summary else "No data"
        st.metric("Quality status", status)
    with c4:
        st.metric("SQLite tables", len(db.list_tables()))

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Direction</span>', unsafe_allow_html=True)
            st.markdown('<div class="exec-card-title">Objective</div>', unsafe_allow_html=True)
            st.write("Turn tabular data into actionable insights with governed, curated outputs.")
            st.markdown('<div class="exec-card-title">Value</div>', unsafe_allow_html=True)
            st.write(
                "Upload raw files, standardize them automatically, and expose decision-ready metrics."
            )

    with right:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Data context</span>', unsafe_allow_html=True)
            st.markdown('<div class="exec-card-title">Data Status</div>', unsafe_allow_html=True)
            if df is not None and not df.empty and quality_summary:
                st.write(f"Dataset: **{st.session_state.data_name}**")
                st.write(f"Curated rows: **{quality_summary['rows']:,}**")
                st.write(f"Columns: **{quality_summary['columns']}**")
                st.write(f"Completeness: **{quality_summary['completeness_pct']:.2f}%**")
            else:
                st.info("No dataset loaded.")

    s1, s2, s3 = st.columns(3)
    if df is not None and not df.empty and quality_summary:
        insight_msg = (
            f"Curated dataset with {quality_summary['numeric_columns']} numeric columns and "
            f"quality score {quality_summary['quality_score']:.0f}/100."
        )
        risk_msg = (
            f"Missing: {quality_summary['missing_pct']:.2f}% | "
            f"Duplicates: {quality_summary['duplicate_pct']:.2f}%."
        )
        action_msg = (
            priority_actions[0] if priority_actions else "Persist curated outputs in SQLite."
        )
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

    st.markdown("### Automated Curation Highlights")
    d1, d2 = st.columns(2)
    with d1:
        with st.container(border=True):
            st.markdown("#### Product Value")
            st.write("- Smart curation standardizes names, types, nulls, and duplicates.")
            st.write("- Quality scoring translates technical data issues into business risk.")
            st.write("- EDA is connected to a reusable profiling layer, not isolated charts.")
    with d2:
        with st.container(border=True):
            st.markdown("#### Engineering Signals")
            st.write(
                "- Layered architecture with explicit analytics, data, and dashboard concerns."
            )
            st.write("- Structured logging with trace id and page timing.")
            st.write("- Tests, lint, preflight, and provenance gates remain active.")

    maturity = quality_summary["quality_score"] if quality_summary else 0
    st.markdown("### Analytics Maturity")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.caption("Data Reliability")
        st.progress(int(min(100, maturity)))
    with m2:
        st.caption("Production Readiness")
        st.progress(90)
    with m3:
        st.caption("Executive Clarity")
        st.progress(92)

    if analysis:
        st.markdown("### Automated Insights")
        for insight in analysis.get("insights", [])[:4]:
            st.write(f"- {insight}")

    if df is not None and not df.empty and {"categoria", "valor_total"}.issubset(df.columns):
        category_revenue = (
            df.groupby("categoria", dropna=False)["valor_total"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig = px.bar(
            category_revenue,
            x="valor_total",
            y="categoria",
            orientation="h",
            title="Top Categories by Revenue",
            labels={"categoria": "product_category", "valor_total": "revenue"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")


def render_upload(db: SQLiteManager, quality_summary: dict[str, Any] | None) -> None:
    st.subheader("Data Upload")
    st.caption(
        "Load a demo dataset or upload CSV/XLSX. The dashboard applies smart curation automatically."
    )

    demo_col_1, demo_col_2 = st.columns(2)
    with demo_col_1:
        if st.button(
            "Load default demo (12 rows)", key="load_default_demo_button", width="stretch"
        ):
            df_demo = load_default_demo_data()
            if df_demo.empty:
                st.error("default_demo.csv not found in data/sample.")
            else:
                apply_dataset_to_session(df_demo, "default_demo.csv", "sample_manual")
                st.success("Loaded and curated default_demo.csv.")
                st.rerun()
    with demo_col_2:
        if st.button("Load large demo (240 rows)", key="load_large_demo_button", width="stretch"):
            df_large = load_large_demo_data()
            if df_large.empty:
                st.error("sample_large.csv not found in data/sample.")
            else:
                apply_dataset_to_session(df_large, "sample_large.csv", "sample_manual")
                st.success("Loaded and curated sample_large.csv.")
                st.rerun()

    if quality_summary:
        st.markdown("### Current curated dataset")
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            st.metric("Quality Score", f"{quality_summary['quality_score']:.0f}/100")
        with q2:
            st.metric("Completeness", f"{quality_summary['completeness_pct']:.1f}%")
        with q3:
            st.metric("Duplicates", int(quality_summary["duplicate_count"]))
        with q4:
            st.metric("Memory", f"{quality_summary['memory_mb']:.2f} MB")

    st.markdown("---")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    if uploaded is None:
        st.info("Upload a file to replace the current dataset.")
        return

    try:
        if uploaded.name.lower().endswith(".csv"):
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

    apply_dataset_to_session(df, uploaded.name, "upload")
    curated_df = st.session_state.data
    curated_summary = st.session_state.quality_summary

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Raw rows", f"{df.shape[0]:,}")
    with k2:
        st.metric("Curated rows", f"{curated_df.shape[0]:,}")
    with k3:
        st.metric("Columns", curated_df.shape[1])
    with k4:
        st.metric("Quality Score", f"{curated_summary['quality_score']:.0f}/100")

    st.success(f"File loaded and curated successfully: {uploaded.name}")
    st.caption("Curated preview (first 50 rows)")
    st.dataframe(curated_df.head(50), width="stretch")

    table_name = st.text_input(
        "SQLite table name",
        value=uploaded.name.replace(".", "_"),
        key="upload_table_name",
    )
    if st.button("Save curated dataset to SQLite", key="save_sqlite_button", width="stretch"):
        ok = db.df_to_sql(curated_df, table_name)
        if ok:
            st.success(f"Table saved: {table_name}")
        else:
            st.error("Failed to save table to SQLite.")


def render_data_preview(
    df: pd.DataFrame | None,
    raw_df: pd.DataFrame | None,
    transform_log: list[dict[str, Any]],
) -> None:
    st.subheader("Data Preview")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Curated Sample", "Raw Sample", "Column Profile", "Curation Log"]
    )

    with tab1:
        st.caption("Curated preview (first 200 rows)")
        st.dataframe(df.head(200), width="stretch")

    with tab2:
        if raw_df is not None and not raw_df.empty:
            st.caption("Raw preview (first 200 rows)")
            st.dataframe(raw_df.head(200), width="stretch")
        else:
            st.info("No raw dataset stored in the session.")

    with tab3:
        info = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Missing": df.isna().sum().values,
                "Unique": [df[c].nunique(dropna=True) for c in df.columns],
            }
        )
        st.dataframe(info, width="stretch")

    with tab4:
        for item in summarize_transformation_log(transform_log):
            st.write(f"- {item}")


def render_eda(
    df: pd.DataFrame | None,
    analysis: dict[str, Any] | None,
    quality_summary: dict[str, Any] | None,
) -> None:
    st.subheader("Exploratory Analysis")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    numeric = df.select_dtypes(include="number")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Rows", f"{len(df):,}")
    with c2:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with c3:
        st.metric("Duplicate rows", int(df.duplicated().sum()))
    with c4:
        score = quality_summary["quality_score"] if quality_summary else 0
        st.metric("Quality Score", f"{score:.0f}/100")

    tab_insights, tab_stats, tab_corr, tab_missing = st.tabs(
        ["Insights", "Statistics", "Correlation", "Missing Profile"]
    )

    with tab_insights:
        if analysis:
            for insight in analysis.get("insights", []):
                st.write(f"- {insight}")
        else:
            st.info("Analysis report not available.")

    with tab_stats:
        if numeric.empty:
            st.info("No numeric columns available for descriptive statistics.")
        else:
            st.dataframe(numeric.describe().T, width="stretch")

    with tab_corr:
        if numeric.shape[1] > 1:
            corr = numeric.corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("At least 2 numeric columns are required.")

    with tab_missing:
        missing_profile = (
            pd.DataFrame(
                {
                    "column": df.columns,
                    "missing_count": df.isna().sum().values,
                    "missing_pct": (df.isna().mean() * 100).values,
                }
            )
            .sort_values(["missing_count", "column"], ascending=[False, True])
            .reset_index(drop=True)
        )
        st.dataframe(missing_profile, width="stretch")


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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")


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
    st.dataframe(preview, width="stretch")


def render_settings(
    df: pd.DataFrame | None,
    quality_summary: dict[str, Any] | None,
    transform_log: list[dict[str, Any]],
) -> None:
    st.subheader("Settings and Runtime")
    st.json(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
            "quality_summary": quality_summary,
            "sqlite_path": str(Settings.SQLITE_PATH),
            "transformations": len(transform_log),
        }
    )

    if transform_log:
        st.markdown("### Transformation Summary")
        for item in summarize_transformation_log(transform_log):
            st.write(f"- {item}")


def main() -> None:
    trace_id = new_trace_id()
    ensure_session_defaults()
    apply_executive_style()
    db = get_db()
    df = st.session_state.data
    raw_df = st.session_state.raw_data
    analysis = st.session_state.analysis
    transform_log = st.session_state.transform_log
    quality_summary = st.session_state.quality_summary
    priority_actions = st.session_state.priority_actions

    APP_LOGGER.info(
        "app_start",
        extra={
            "trace_id": trace_id,
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
            "quality_score": quality_summary["quality_score"] if quality_summary else None,
        },
    )

    render_header(df, quality_summary)
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
            st.caption(f"Curated rows: {df.shape[0]:,}")
            st.caption(f"Columns: {df.shape[1]}")
            if raw_df is not None:
                st.caption(f"Raw rows: {raw_df.shape[0]:,}")
            if quality_summary:
                st.caption(f"Quality score: **{quality_summary['quality_score']:.0f}/100**")
                st.caption(f"Status: **{quality_summary['status']}**")
            if st.session_state.data_source == "sample_auto":
                st.info("Default demo dataset loaded automatically.")

        st.link_button(
            "PT-BR version",
            "https://github.com/samuelmaia-analytics/data-senior-analytics/blob/main/README.md",
            use_container_width=True,
        )

        if st.button("Reset session", width="stretch"):
            clear_dataset_state()
            st.rerun()

    page_handlers = {
        "Overview": lambda: render_home(df, db, quality_summary, analysis, priority_actions),
        "Upload": lambda: render_upload(db, quality_summary),
        "Data": lambda: render_data_preview(df, raw_df, transform_log),
        "EDA": lambda: render_eda(df, analysis, quality_summary),
        "Visualizations": lambda: render_charts(df),
        "Database": lambda: render_database(db),
        "Settings": lambda: render_settings(df, quality_summary, transform_log),
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
