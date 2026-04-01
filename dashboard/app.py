"""Streamlit dashboard with a curated analytics workflow."""

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
    build_business_snapshot,
    build_decision_brief,
    build_governance_snapshot,
    summarize_correlation_pairs,
    summarize_transformation_log,
)
from src.app.curation_service import curate_dataset  # noqa: E402
from src.app.privacy_guard import mask_sensitive_dataframe  # noqa: E402
from src.data.sqlite_manager import SQLiteManager  # noqa: E402
from src.utils.observability import (  # noqa: E402
    get_structured_logger,
    new_trace_id,
    timed_stage,
)

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


def apply_dashboard_style() -> None:
    st.markdown(
        """
        <style>
            :root {
                --surface: rgba(255, 255, 255, 0.94);
                --surface-alt: rgba(248, 250, 252, 0.95);
                --text-main: #0f172a;
                --text-muted: #475569;
                --line: #d8dee8;
                --accent: #0b4e6e;
                --accent-soft: rgba(11, 78, 110, 0.12);
                --warn: #b45309;
                --good: #166534;
                --danger: #991b1b;
            }
            html, body, [class*="css"] {
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(11, 78, 110, 0.14), transparent 26%),
                    radial-gradient(circle at top right, rgba(180, 83, 9, 0.16), transparent 22%),
                    linear-gradient(180deg, #f8fbfd 0%, #eef3f7 100%);
            }
            .main .block-container {
                max-width: 1240px;
                padding-top: 1.2rem;
                padding-bottom: 2rem;
            }
            .hero {
                padding: 1.15rem 1.3rem;
                border: 1px solid var(--line);
                border-radius: 18px;
                background:
                    radial-gradient(circle at top right, rgba(180, 83, 9, 0.10), transparent 22%),
                    linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
                box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
                margin-bottom: 0.9rem;
            }
            .hero-title {
                margin: 0;
                color: var(--text-main);
                font-size: 2.15rem;
                font-weight: 750;
                letter-spacing: -0.02em;
            }
            .hero-subtitle {
                margin: 0.35rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.95rem;
            }
            div[data-testid="stMetric"] {
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 14px;
                padding: 0.5rem 0.75rem;
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
            }
            div[role="radiogroup"] > label {
                border: 1px solid var(--line);
                border-radius: 12px;
                padding: 0.22rem 0.6rem;
                background: #ffffff;
                margin-right: 0.2rem;
            }
            .exec-pill {
                display: inline-block;
                padding: 0.2rem 0.55rem;
                border-radius: 999px;
                border: 1px solid #cbd5e1;
                color: var(--text-main);
                font-size: 0.78rem;
                background: #f8fafc;
                margin-bottom: 0.4rem;
            }
            .exec-card-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: var(--text-main);
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
            .board-card {
                padding: 1rem 1.05rem;
                border-radius: 16px;
                border: 1px solid #d5dee8;
                background: linear-gradient(160deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.92) 100%);
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
                min-height: 168px;
            }
            .board-kicker {
                margin: 0 0 0.45rem 0;
                color: var(--accent);
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            .board-title {
                margin: 0 0 0.45rem 0;
                color: var(--text-main);
                font-size: 1.1rem;
                font-weight: 760;
            }
            .board-copy {
                margin: 0;
                color: var(--text-muted);
                font-size: 0.92rem;
                line-height: 1.45;
            }
            .signal-card {
                padding: 1rem 1.05rem;
                border-radius: 18px;
                border: 1px solid var(--line);
                background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
                min-height: 180px;
            }
            .signal-kicker {
                margin: 0 0 0.5rem 0;
                color: var(--accent);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.72rem;
                font-weight: 700;
            }
            .signal-title {
                margin: 0 0 0.55rem 0;
                color: var(--text-main);
                font-size: 1.22rem;
                font-weight: 760;
            }
            .signal-copy {
                margin: 0;
                color: var(--text-muted);
                line-height: 1.5;
                font-size: 0.94rem;
            }
            .status-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.75rem;
                margin: 0.25rem 0 1rem 0;
            }
            .status-card {
                padding: 0.9rem 1rem;
                border-radius: 16px;
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.94);
            }
            .status-label {
                margin: 0 0 0.35rem 0;
                color: var(--text-muted);
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }
            .status-value {
                margin: 0;
                color: var(--text-main);
                font-size: 1.15rem;
                font-weight: 760;
            }
            .status-caption {
                margin: 0.3rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.86rem;
            }
            @media (max-width: 960px) {
                .status-strip {
                    grid-template-columns: 1fr 1fr;
                }
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


def format_currency(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_compact_number(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    if abs(float(value)) >= 1_000_000:
        return f"{float(value) / 1_000_000:.1f}M"
    if abs(float(value)) >= 1_000:
        return f"{float(value) / 1_000:.1f}K"
    return f"{float(value):,.0f}"


def apply_dataset_to_session(df: pd.DataFrame, data_name: str, data_source: str) -> None:
    """Persist raw data, curated data, and metadata in the active session."""
    artifacts = curate_dataset(df)
    business_snapshot = getattr(artifacts, "business_snapshot", None)
    if business_snapshot is None:
        business_snapshot = getattr(artifacts, "executive_snapshot", None)
    if business_snapshot is None:
        business_snapshot = build_business_snapshot(artifacts.curated_df)

    st.session_state.raw_data = artifacts.raw_df
    st.session_state.data = artifacts.curated_df
    st.session_state.data_name = data_name
    st.session_state.data_source = data_source
    st.session_state.loaded_at = datetime.now().isoformat(timespec="seconds")
    st.session_state.analysis = artifacts.analysis
    st.session_state.transform_log = artifacts.transform_log
    st.session_state.quality_summary = artifacts.quality_summary
    st.session_state.priority_actions = artifacts.priority_actions
    st.session_state.business_snapshot = business_snapshot
    st.session_state.privacy_snapshot = artifacts.privacy_snapshot
    st.session_state.masked_data = artifacts.masked_curated_df


def clear_dataset_state() -> None:
    for key in (
        "raw_data",
        "data",
        "data_name",
        "data_source",
        "loaded_at",
        "analysis",
        "transform_log",
        "quality_summary",
        "priority_actions",
        "business_snapshot",
        "privacy_snapshot",
        "masked_data",
    ):
        if key in st.session_state:
            del st.session_state[key]


def ensure_session_defaults() -> None:
    defaults = {
        "raw_data": None,
        "data": None,
        "data_name": None,
        "data_source": None,
        "loaded_at": None,
        "analysis": None,
        "transform_log": [],
        "quality_summary": None,
        "priority_actions": [],
        "business_snapshot": None,
        "privacy_snapshot": None,
        "masked_data": None,
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
            <p class="hero-subtitle">Dashboard for diagnostics, curation, exploration, and decision support.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
    with c1:
        st.metric("Environment", "Production")
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
            <span class="exec-chip">Decision workflow</span>
            <span class="exec-chip">Curated ingestion</span>
            <span class="exec-chip">Trust signals</span>
            <span class="exec-chip">Operational persistence</span>
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
    business_snapshot: dict[str, Any] | None,
    governance_snapshot: dict[str, Any],
    privacy_snapshot: dict[str, Any] | None,
) -> None:
    st.subheader("Summary")
    purged_datasets = db.purge_expired_datasets()
    decision_brief = build_decision_brief(
        quality_summary=quality_summary,
        business_snapshot=business_snapshot,
        priority_actions=priority_actions,
        analysis=analysis,
    )

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

    if business_snapshot:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Revenue", format_currency(business_snapshot["revenue"]))
        with k2:
            st.metric("Average ticket", format_currency(business_snapshot["avg_ticket"]))
        with k3:
            st.metric(
                "Unique clients",
                format_compact_number(business_snapshot["unique_clients"]),
            )
        with k4:
            st.metric("Items sold", format_compact_number(business_snapshot["items_sold"]))

    expiring_registry = db.get_expiring_datasets(within_days=14)
    governance_metrics = st.columns(4)
    with governance_metrics[0]:
        st.metric("Registered datasets", len(db.get_dataset_registry()))
    with governance_metrics[1]:
        st.metric("Expiring in 14d", len(expiring_registry))
    with governance_metrics[2]:
        st.metric("Purged now", purged_datasets)
    with governance_metrics[3]:
        personal_datasets = 0
        registry = db.get_dataset_registry()
        if not registry.empty:
            personal_datasets = int(registry["contains_personal_data"].fillna(0).sum())
        st.metric("Datasets with personal data", personal_datasets)

    st.markdown(
        f"""
        <div class="status-strip">
            <div class="status-card">
                <p class="status-label">Decision Risk</p>
                <p class="status-value">{decision_brief['decision_risk']}</p>
                <p class="status-caption">Current release posture for business-facing use.</p>
            </div>
            <div class="status-card">
                <p class="status-label">Confidence</p>
                <p class="status-value">{decision_brief['confidence_label']}</p>
                <p class="status-caption">Trust level based on quality gates and data coverage.</p>
            </div>
            <div class="status-card">
                <p class="status-label">Release</p>
                <p class="status-value">{governance_snapshot['release_label']}</p>
                <p class="status-caption">Operational recommendation for sharing or persistence.</p>
            </div>
            <div class="status-card">
                <p class="status-label">Source</p>
                <p class="status-value">{governance_snapshot['data_source_label']}</p>
                <p class="status-caption">{governance_snapshot['data_name']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(
            f"""
            <div class="signal-card">
                <p class="signal-kicker">Leadership view</p>
                <h3 class="signal-title">{decision_brief['headline']}</h3>
                <p class="signal-copy">{decision_brief['primary_concern']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Governance</span>', unsafe_allow_html=True)
            st.markdown(
                '<div class="exec-card-title">Trust and recency</div>', unsafe_allow_html=True
            )
            st.write(f"Trust label: **{governance_snapshot['trust_label']}**")
            st.write(f"Loaded at: **{governance_snapshot['loaded_at'] or 'Unavailable'}**")
            st.write(f"Latest record: **{governance_snapshot['latest_record'] or 'Unavailable'}**")
            st.write(f"Transformations logged: **{governance_snapshot['transformation_count']}**")
            if privacy_snapshot:
                st.write(f"LGPD risk: **{privacy_snapshot['risk_level']}**")
                st.write(
                    f"Personal columns detected: **{len(privacy_snapshot['personal_columns'])}**"
                )

    s1, s2, s3 = st.columns(3)
    if df is not None and not df.empty and quality_summary:
        insight_msg = (
            decision_brief["drivers"][0]
            if decision_brief["drivers"]
            else (f"Curated dataset with {quality_summary['numeric_columns']} numeric columns.")
        )
        risk_msg = (
            f"Quality score {quality_summary['quality_score']:.0f}/100 | "
            f"Missing {quality_summary['missing_pct']:.2f}% | "
            f"Duplicates {quality_summary['duplicate_pct']:.2f}%."
        )
        action_msg = decision_brief["recommended_action"]
    else:
        insight_msg = "No active dataset to generate decision-ready insights."
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

    if decision_brief["drivers"]:
        st.markdown("### Decision Drivers")
        for driver in decision_brief["drivers"]:
            st.write(f"- {driver}")

    if privacy_snapshot and privacy_snapshot["personal_data_detected"]:
        st.markdown("### Privacy and Governance")
        st.warning(
            "The current dataset appears to contain personal data. Previews are masked and "
            "persistence should follow minimization and lawful-basis review."
        )
        for control in privacy_snapshot["controls"]:
            st.write(f"- {control}")

    if not expiring_registry.empty:
        st.markdown("### Retention Watch")
        st.dataframe(expiring_registry.head(10), width="stretch")

    if business_snapshot:
        st.markdown("### Business Briefing")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown(
                f"""
                <div class="board-card">
                    <p class="board-kicker">Commercial Focus</p>
                    <h3 class="board-title">Top category: {business_snapshot['top_category'] or 'N/A'}</h3>
                    <p class="board-copy">
                        Revenue concentration is led by the strongest category at
                        {business_snapshot['top_category_share'] or 0:.1f}% of revenue.
                        Use this signal to prioritize pricing, portfolio defense, and cross-sell actions.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b2:
            st.markdown(
                f"""
                <div class="board-card">
                    <p class="board-kicker">Regional Signal</p>
                    <h3 class="board-title">Top region: {business_snapshot['top_region'] or 'N/A'}</h3>
                    <p class="board-copy">
                        Regional mix shows the largest revenue share at
                        {business_snapshot['top_region_share'] or 0:.1f}%.
                        This helps focus field execution, service quality review, and distribution gaps.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b3:
            st.markdown(
                f"""
                <div class="board-card">
                    <p class="board-kicker">Momentum</p>
                    <h3 class="board-title">{business_snapshot['trend_direction']}</h3>
                    <p class="board-copy">
                        Latest visible period change:
                        {business_snapshot['trend_change_pct'] if business_snapshot['trend_change_pct'] is not None else 0:.1f}%.
                        This is the fastest indicator for whether commercial momentum is improving or softening.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
        st.caption("Decision Clarity")
        st.progress(92)

    if analysis:
        st.markdown("### Automated Insights")
        for insight in analysis.get("insights", [])[:4]:
            st.write(f"- {insight}")

    if business_snapshot and not business_snapshot["revenue_by_category"].empty:
        chart_left, chart_right = st.columns([1.1, 1])
        category_revenue = business_snapshot["revenue_by_category"].head(10)
        fig = px.bar(
            category_revenue,
            x="valor_total",
            y="categoria",
            orientation="h",
            title="Top Categories by Revenue",
            labels={"categoria": "product_category", "valor_total": "revenue"},
            text="share_pct",
            color="share_pct",
            color_continuous_scale=["#dbeafe", "#0b4e6e"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        with chart_left:
            st.plotly_chart(fig, width="stretch")

        with chart_right:
            region_df = business_snapshot["revenue_by_region"]
            if isinstance(region_df, pd.DataFrame) and not region_df.empty:
                region_fig = px.pie(
                    region_df.head(6),
                    names="regiao",
                    values="valor_total",
                    title="Revenue Mix by Region",
                    hole=0.58,
                    color_discrete_sequence=[
                        "#0b4e6e",
                        "#1d6f91",
                        "#3b92b5",
                        "#8bbfd3",
                        "#c7e3ef",
                        "#d97706",
                    ],
                )
                region_fig.update_traces(textinfo="label+percent")
                st.plotly_chart(region_fig, width="stretch")
            else:
                st.info("Regional mix is not available for the current dataset.")

        trend_df = business_snapshot["revenue_trend"]
        if isinstance(trend_df, pd.DataFrame) and not trend_df.empty:
            trend_fig = px.area(
                trend_df,
                x="data",
                y="valor_total",
                title="Revenue Trend",
                labels={"data": "date", "valor_total": "revenue"},
                color_discrete_sequence=["#0b4e6e"],
            )
            trend_fig.update_traces(mode="lines+markers", line={"width": 3}, opacity=0.78)
            st.plotly_chart(trend_fig, width="stretch")
        else:
            st.info("Revenue trend is not available for the current dataset.")


def render_upload(db: SQLiteManager, quality_summary: dict[str, Any] | None) -> None:
    st.subheader("Data Upload")
    st.caption(
        "Load a demo dataset or upload CSV/XLSX. The dashboard applies smart curation automatically."
    )

    demo_col_1, demo_col_2 = st.columns(2)
    with demo_col_1:
        if st.button(
            "Load default demo (12 rows)",
            key="load_default_demo_button",
            width="stretch",
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
    privacy_snapshot = st.session_state.privacy_snapshot
    masked_df = st.session_state.masked_data

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
    if privacy_snapshot and privacy_snapshot["personal_data_detected"]:
        st.caption("Masked curated preview (first 50 rows)")
        st.dataframe(masked_df.head(50), width="stretch")
        st.info(
            f"LGPD control active. Personal columns detected: {', '.join(privacy_snapshot['personal_columns'])}."
        )
    else:
        st.caption("Curated preview (first 50 rows)")
        st.dataframe(curated_df.head(50), width="stretch")

    table_name = st.text_input(
        "SQLite table name",
        value=uploaded.name.replace(".", "_"),
        key="upload_table_name",
    )
    persist_masked = st.checkbox(
        "Persist masked dataset",
        value=bool(privacy_snapshot and privacy_snapshot["safe_persistence_default"]),
        key="persist_masked_dataset",
    )
    retention_days = st.selectbox(
        "Retention period",
        options=[30, 90, 180, 365],
        index=1,
        key="retention_days",
    )
    lgpd_ack = st.checkbox(
        "I reviewed lawful basis, minimization, and retention for this dataset",
        value=False,
        key="lgpd_acknowledgement",
    )
    if st.button("Save curated dataset to SQLite", key="save_sqlite_button", width="stretch"):
        if privacy_snapshot and privacy_snapshot["personal_data_detected"] and not lgpd_ack:
            st.error(
                "LGPD safeguard: acknowledge lawful basis and minimization before persisting personal data."
            )
            return
        dataset_to_persist = masked_df if persist_masked else curated_df
        ok = db.df_to_sql(
            dataset_to_persist,
            table_name,
            metadata={
                "retention_days": retention_days,
                "persistence_mode": "masked" if persist_masked else "curated",
                "contains_personal_data": bool(
                    privacy_snapshot and privacy_snapshot["personal_data_detected"]
                ),
                "contains_sensitive_data": bool(
                    privacy_snapshot and privacy_snapshot["sensitive_data_detected"]
                ),
                "legal_basis_acknowledged": bool(lgpd_ack),
                "privacy_risk_level": (
                    privacy_snapshot["risk_level"] if privacy_snapshot else "Minimal"
                ),
                "source_name": st.session_state.data_name,
                "data_source": st.session_state.data_source,
                "personal_columns": (
                    privacy_snapshot["personal_columns"] if privacy_snapshot else []
                ),
                "sensitive_columns": (
                    privacy_snapshot["sensitive_columns"] if privacy_snapshot else []
                ),
            },
        )
        if ok:
            st.success(f"Table saved: {table_name}")
        else:
            st.error("Failed to save table to SQLite.")


def render_data_preview(
    df: pd.DataFrame | None,
    raw_df: pd.DataFrame | None,
    transform_log: list[dict[str, Any]],
    privacy_snapshot: dict[str, Any] | None,
    masked_df: pd.DataFrame | None,
) -> None:
    st.subheader("Data Preview")
    if df is None or df.empty:
        st.warning("No data available.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Curated Sample", "Raw Sample", "Column Profile", "Curation Log"]
    )

    with tab1:
        if (
            privacy_snapshot
            and privacy_snapshot["personal_data_detected"]
            and masked_df is not None
        ):
            st.caption("Masked curated preview (first 200 rows)")
            st.dataframe(masked_df.head(200), width="stretch")
        else:
            st.caption("Curated preview (first 200 rows)")
            st.dataframe(df.head(200), width="stretch")

    with tab2:
        if raw_df is not None and not raw_df.empty:
            if privacy_snapshot and privacy_snapshot["personal_data_detected"]:
                st.caption("Masked raw preview (first 200 rows)")
                masked_raw = mask_sensitive_dataframe(
                    raw_df.head(200), privacy_snapshot["personal_columns"]
                )
                st.dataframe(masked_raw, width="stretch")
            else:
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
        if privacy_snapshot and privacy_snapshot["personal_data_detected"]:
            st.write(
                f"- Privacy controls active for columns: {', '.join(privacy_snapshot['personal_columns'])}."
            )


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
            strongest_pairs = summarize_correlation_pairs(df)
            if not strongest_pairs.empty:
                st.caption("Strongest relationships")
                st.dataframe(strongest_pairs, width="stretch")
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

    tabs = st.tabs(["Distribution", "Business Mix", "Trend"])

    with tabs[0]:
        if numeric_cols:
            col = st.selectbox("Numeric variable", numeric_cols, key="chart_numeric_variable")
            fig = px.histogram(
                df,
                x=col,
                nbins=30,
                title=f"Distribution: {col}",
                color_discrete_sequence=["#0b4e6e"],
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No numeric columns available.")

    with tabs[1]:
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
            fig = px.bar(
                grouped.head(15),
                x=cat,
                y=val,
                title=f"Average {val} by {cat}",
                color=val,
                color_continuous_scale=["#dbeafe", "#0b4e6e"],
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Category and numeric columns are required.")

    with tabs[2]:
        if {"data", "valor_total"}.issubset(df.columns):
            trend_df = (
                df.assign(data=pd.to_datetime(df["data"], errors="coerce"))
                .dropna(subset=["data"])
                .groupby("data", dropna=False)["valor_total"]
                .sum()
                .reset_index()
                .sort_values("data")
            )
            trend_fig = px.area(
                trend_df,
                x="data",
                y="valor_total",
                title="Revenue over time",
                labels={"data": "date", "valor_total": "revenue"},
                color_discrete_sequence=["#0b4e6e"],
            )
            st.plotly_chart(trend_fig, width="stretch")
        else:
            st.info("Trend view requires `data` and `valor_total` columns.")


def render_database(db: SQLiteManager, privacy_snapshot: dict[str, Any] | None) -> None:
    st.subheader("SQLite Database")
    tables = db.list_tables()
    if not tables:
        st.info("No tables found in SQLite.")
    registry = db.get_dataset_registry()
    if not registry.empty:
        st.markdown("### Persistence Registry")
        st.dataframe(registry, width="stretch")

    if not tables:
        return

    table = st.selectbox("Table", tables, key="database_table")
    count = db.fetch_scalar(f"SELECT COUNT(*) FROM [{table}]") or 0
    st.metric("Rows in table", int(count))

    preview = db.sql_to_df(f"SELECT * FROM [{table}] LIMIT 500")
    st.caption("Table preview (up to 500 rows)")
    if privacy_snapshot and privacy_snapshot["personal_data_detected"]:
        masked_preview = mask_sensitive_dataframe(preview, privacy_snapshot["personal_columns"])
        st.dataframe(masked_preview, width="stretch")
    else:
        st.dataframe(preview, width="stretch")

    audit_log = db.get_dataset_audit_log(table)
    if not audit_log.empty:
        st.markdown("### Audit Log")
        st.dataframe(audit_log, width="stretch")


def render_settings(
    df: pd.DataFrame | None,
    quality_summary: dict[str, Any] | None,
    transform_log: list[dict[str, Any]],
    privacy_snapshot: dict[str, Any] | None,
) -> None:
    st.subheader("Settings and Runtime")
    db = get_db()
    governance_snapshot = build_governance_snapshot(
        df=df,
        quality_summary=quality_summary,
        transform_log=transform_log,
        data_name=st.session_state.data_name,
        data_source=st.session_state.data_source,
        loaded_at=st.session_state.loaded_at,
    )
    st.json(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
            "quality_summary": quality_summary,
            "governance_snapshot": governance_snapshot,
            "privacy_snapshot": (
                {
                    "risk_level": privacy_snapshot["risk_level"],
                    "personal_columns": privacy_snapshot["personal_columns"],
                    "sensitive_columns": privacy_snapshot["sensitive_columns"],
                    "safe_persistence_default": privacy_snapshot["safe_persistence_default"],
                }
                if privacy_snapshot
                else None
            ),
            "sqlite_path": str(Settings.SQLITE_PATH),
            "transformations": len(transform_log),
            "registered_datasets": int(len(db.get_dataset_registry())),
        }
    )

    if transform_log:
        st.markdown("### Transformation Summary")
        for item in summarize_transformation_log(transform_log):
            st.write(f"- {item}")


def main() -> None:
    trace_id = new_trace_id()
    ensure_session_defaults()
    apply_dashboard_style()
    db = get_db()
    df = st.session_state.data
    raw_df = st.session_state.raw_data
    analysis = st.session_state.analysis
    transform_log = st.session_state.transform_log
    quality_summary = st.session_state.quality_summary
    priority_actions = st.session_state.priority_actions
    business_snapshot = st.session_state.business_snapshot
    privacy_snapshot = st.session_state.privacy_snapshot
    masked_df = st.session_state.masked_data
    governance_snapshot = build_governance_snapshot(
        df=df,
        quality_summary=quality_summary,
        transform_log=transform_log,
        data_name=st.session_state.data_name,
        data_source=st.session_state.data_source,
        loaded_at=st.session_state.loaded_at,
    )

    APP_LOGGER.info(
        "app_start",
        extra={
            "trace_id": trace_id,
            "data_source": st.session_state.data_source,
            "data_name": st.session_state.data_name,
            "rows": int(df.shape[0]) if df is not None else 0,
            "columns": int(df.shape[1]) if df is not None else 0,
            "quality_score": (quality_summary["quality_score"] if quality_summary else None),
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
            st.caption(f"Release: **{governance_snapshot['release_label']}**")
            st.caption(f"Trust: **{governance_snapshot['trust_label']}**")
            if privacy_snapshot:
                st.caption(f"LGPD risk: **{privacy_snapshot['risk_level']}**")
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
        "Overview": lambda: render_home(
            df,
            db,
            quality_summary,
            analysis,
            priority_actions,
            business_snapshot,
            governance_snapshot,
            privacy_snapshot,
        ),
        "Upload": lambda: render_upload(db, quality_summary),
        "Data": lambda: render_data_preview(df, raw_df, transform_log, privacy_snapshot, masked_df),
        "EDA": lambda: render_eda(df, analysis, quality_summary),
        "Visualizations": lambda: render_charts(df),
        "Database": lambda: render_database(db, privacy_snapshot),
        "Settings": lambda: render_settings(df, quality_summary, transform_log, privacy_snapshot),
    }

    try:
        with timed_stage(f"render_page:{page}") as timer:
            page_handlers[page]()
        APP_LOGGER.info(
            "page_rendered",
            extra={
                "trace_id": trace_id,
                "page": page,
                "elapsed_ms": round(timer.elapsed_ms, 2),
            },
        )
    except Exception as exc:  # noqa: BLE001
        APP_LOGGER.error(
            "page_render_failed",
            extra={"trace_id": trace_id, "page": page, "error": str(exc)},
        )
        st.error("Failed to render this page. The app is still available.")
        st.exception(exc)


if __name__ == "__main__":
    main()
