"""Streamlit app rebuilt with a clean executive layout and stable data flow."""

from __future__ import annotations

import os
import sys
import subprocess
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

PAGE_OPTIONS = [
    "Home",
    "Upload",
    "Data Preview",
    "Exploratory Analysis",
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

@st.cache_resource
def get_db() -> SQLiteManager:
    return SQLiteManager()


@st.cache_data
def load_default_demo_data() -> pd.DataFrame:
    demo_path = Settings.SAMPLE_DATA_DIR / "default_demo.csv"
    if demo_path.exists():
        return pd.read_csv(demo_path)
    return pd.DataFrame()


def ensure_session_defaults() -> None:
    if "data" not in st.session_state:
        st.session_state.data = None
    if "data_name" not in st.session_state:
        st.session_state.data_name = None
    if "data_source" not in st.session_state:
        st.session_state.data_source = None
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"

    if st.session_state.data is None:
        demo_df = load_default_demo_data()
        if not demo_df.empty:
            st.session_state.data = demo_df
            st.session_state.data_name = "default_demo.csv"
            st.session_state.data_source = "sample_auto"


def render_header() -> None:
    st.title("Data Senior Analytics")
    st.caption("Senior-level analytics dashboard for business decision support")


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


def render_home(df: pd.DataFrame | None, db: SQLiteManager) -> None:
    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Python", "3.11+")
    with col2:
        st.metric("Framework", "Streamlit")
    with col3:
        st.metric("Source", "Kaggle")
    with col4:
        st.metric("Tables", len(db.list_tables()))

    left, right = st.columns(2)
    with left:
        st.markdown("### Business Goal")
        st.write("Transform raw datasets into validated analytical insights for faster decisions.")

    with right:
        st.markdown("### Current Data Status")
        if df is not None and not df.empty:
            st.write(f"Dataset: **{st.session_state.data_name}**")
            st.write(f"Rows: **{df.shape[0]:,}**")
            st.write(f"Columns: **{df.shape[1]}**")
        else:
            st.write("No dataset loaded yet.")


def render_upload(db: SQLiteManager) -> None:
    st.subheader("Data Upload")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    if uploaded is None:
        st.info("Upload a file to replace the default demo dataset.")
        return

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.session_state.data = df
    st.session_state.data_name = uploaded.name
    st.session_state.data_source = "upload"

    st.success(f"Loaded: {uploaded.name}")
    st.caption("Preview (first 50 rows)")
    st.table(df.head(50))

    table_name = st.text_input(
        "SQLite table name",
        value=uploaded.name.replace(".", "_"),
        key="upload_table_name",
    )
    if st.button("Save to SQLite", key="save_sqlite_button"):
        ok = db.df_to_sql(df, table_name)
        if ok:
            st.success(f"Saved to table: {table_name}")
        else:
            st.error("Failed to save data to SQLite.")


def render_data_preview(df: pd.DataFrame | None) -> None:
    st.subheader("Data Preview")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    st.caption("Preview (first 200 rows)")
    st.table(df.head(200))

    info = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "missing": df.isna().sum().values,
            "unique": [df[c].nunique(dropna=True) for c in df.columns],
        }
    )
    st.markdown("### Column Profile")
    st.table(info)


def render_eda(df: pd.DataFrame | None) -> None:
    st.subheader("Exploratory Analysis")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    numeric = df.select_dtypes(include="number")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with col3:
        st.metric("Duplicate rows", int(df.duplicated().sum()))

    if numeric.empty:
        st.info("No numeric columns detected for descriptive stats.")
        return

    st.markdown("### Descriptive Statistics")
    st.table(numeric.describe().T)

    if numeric.shape[1] > 1:
        corr = numeric.corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
        st.plotly_chart(fig, use_container_width=True)


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
        cat = st.selectbox("Category", cat_cols, key="chart_category")
        val = st.selectbox(
            "Metric",
            numeric_cols,
            index=min(1, len(numeric_cols) - 1),
            key="chart_metric",
        )
        grouped = df.groupby(cat, dropna=False)[val].mean().reset_index().sort_values(val, ascending=False)
        fig = px.bar(grouped.head(15), x=cat, y=val, title=f"Average {val} by {cat}")
        st.plotly_chart(fig, use_container_width=True)


def render_database(db: SQLiteManager) -> None:
    st.subheader("SQLite Database")
    tables = db.list_tables()
    if not tables:
        st.info("No tables found in SQLite yet.")
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
    ensure_session_defaults()
    db = get_db()
    df = st.session_state.data

    render_header()
    page = st.radio(
        "Navigation",
        PAGE_OPTIONS,
        horizontal=True,
        key="selected_page",
        label_visibility="collapsed",
    )

    with st.sidebar:
        st.markdown("## Active Context")
        st.caption(f"Build: {get_build_id()}")
        st.caption(f"Page: {page}")
        if df is not None and not df.empty:
            st.caption(f"Dataset: {st.session_state.data_name}")
            st.caption(f"Rows: {df.shape[0]:,}")
            st.caption(f"Cols: {df.shape[1]}")
            if st.session_state.data_source == "sample_auto":
                st.info("Default demo dataset loaded.")
        if st.button("Reset session", use_container_width=True):
            for key in ("data", "data_name", "data_source"):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    page_handlers = {
        "Home": lambda: render_home(df, db),
        "Upload": lambda: render_upload(db),
        "Data Preview": lambda: render_data_preview(df),
        "Exploratory Analysis": lambda: render_eda(df),
        "Visualizations": lambda: render_charts(df),
        "Database": lambda: render_database(db),
        "Settings": lambda: render_settings(df),
    }

    try:
        page_handlers[page]()
    except Exception as exc:  # noqa: BLE001
        st.error("This page failed to render. The app remains available.")
        st.exception(exc)


if __name__ == "__main__":
    main()
