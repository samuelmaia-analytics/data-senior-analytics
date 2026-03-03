"""Streamlit app rebuilt with a clean executive layout and stable data flow."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import Settings
from src.data.sqlite_manager import SQLiteManager

st.set_page_config(
    page_title="Data Senior Analytics",
    page_icon="DA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap");

    :root {
        --bg: #f5f7fb;
        --surface: #ffffff;
        --text: #101828;
        --muted: #475467;
        --border: #d0d5dd;
        --brand: #0f172a;
        --accent: #c91c24;
    }

    .stApp {
        font-family: "Manrope", sans-serif;
        background: radial-gradient(circle at 0% 0%, #ffffff 0%, var(--bg) 55%);
        color: var(--text);
    }

    .main .block-container {
        max-width: 1240px;
        padding-top: 1.1rem;
        padding-bottom: 2.2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb !important;
    }

    .app-title {
        margin: 0;
        font-size: clamp(2rem, 3vw, 2.7rem);
        font-weight: 800;
        color: var(--brand);
        letter-spacing: -0.02em;
    }

    .app-subtitle {
        margin: 0.2rem 0 1rem 0;
        color: var(--muted);
        font-size: 0.98rem;
    }

    .panel {
        border: 1px solid var(--border);
        background: var(--surface);
        border-radius: 12px;
        padding: 1rem 1rem 0.4rem 1rem;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.06);
    }

    .stDataFrame, [data-testid="stMetric"] {
        border-radius: 10px;
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


def ensure_session_defaults() -> None:
    if "data" not in st.session_state:
        st.session_state.data = None
    if "data_name" not in st.session_state:
        st.session_state.data_name = None
    if "data_source" not in st.session_state:
        st.session_state.data_source = None

    if st.session_state.data is None:
        demo_df = load_default_demo_data()
        if not demo_df.empty:
            st.session_state.data = demo_df
            st.session_state.data_name = "default_demo.csv"
            st.session_state.data_source = "sample_auto"


def render_header() -> None:
    st.markdown('<h1 class="app-title">Data Senior Analytics</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">Senior-level analytics dashboard for business decision support</p>',
        unsafe_allow_html=True,
    )


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
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Business Goal")
        st.write("Transform raw datasets into validated analytical insights for faster decisions.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### Current Data Status")
        if df is not None and not df.empty:
            st.write(f"Dataset: **{st.session_state.data_name}**")
            st.write(f"Rows: **{df.shape[0]:,}**")
            st.write(f"Columns: **{df.shape[1]}**")
        else:
            st.write("No dataset loaded yet.")
        st.markdown("</div>", unsafe_allow_html=True)


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
    st.dataframe(df.head(50), use_container_width=True)

    table_name = st.text_input("SQLite table name", value=uploaded.name.replace(".", "_"))
    if st.button("Save to SQLite"):
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

    st.dataframe(df.head(200), use_container_width=True)

    info = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "missing": df.isna().sum().values,
            "unique": [df[c].nunique(dropna=True) for c in df.columns],
        }
    )
    st.markdown("### Column Profile")
    st.dataframe(info, use_container_width=True)


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
    st.dataframe(numeric.describe().T, use_container_width=True)

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
        col = st.selectbox("Numeric variable", numeric_cols)
        fig = px.histogram(df, x=col, nbins=30, title=f"Distribution: {col}")
        st.plotly_chart(fig, use_container_width=True)

    if cat_cols and numeric_cols:
        cat = st.selectbox("Category", cat_cols)
        val = st.selectbox("Metric", numeric_cols, index=min(1, len(numeric_cols) - 1))
        grouped = df.groupby(cat, dropna=False)[val].mean().reset_index().sort_values(val, ascending=False)
        fig = px.bar(grouped.head(15), x=cat, y=val, title=f"Average {val} by {cat}")
        st.plotly_chart(fig, use_container_width=True)


def render_database(db: SQLiteManager) -> None:
    st.subheader("SQLite Database")
    tables = db.list_tables()
    if not tables:
        st.info("No tables found in SQLite yet.")
        return

    table = st.selectbox("Table", tables)
    count = db.fetch_scalar(f"SELECT COUNT(*) FROM {table}") or 0
    st.metric("Rows in table", int(count))

    preview = db.sql_to_df(f"SELECT * FROM {table} LIMIT 500")
    st.dataframe(preview, use_container_width=True)


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

    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Go to",
            [
                "Home",
                "Upload",
                "Data Preview",
                "Exploratory Analysis",
                "Visualizations",
                "Database",
                "Settings",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        if df is not None and not df.empty:
            st.markdown("### Active Dataset")
            st.caption(st.session_state.data_name)
            st.caption(f"Rows: {df.shape[0]:,}")
            st.caption(f"Cols: {df.shape[1]}")
            if st.session_state.data_source == "sample_auto":
                st.info("Default demo dataset loaded.")

    render_header()

    if page == "Home":
        render_home(df, db)
    elif page == "Upload":
        render_upload(db)
    elif page == "Data Preview":
        render_data_preview(df)
    elif page == "Exploratory Analysis":
        render_eda(df)
    elif page == "Visualizations":
        render_charts(df)
    elif page == "Database":
        render_database(db)
    elif page == "Settings":
        render_settings(df)


main()
