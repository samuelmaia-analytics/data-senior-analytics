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

PAGE_OPTIONS = [
    "Resumo",
    "Upload",
    "Dados",
    "EDA",
    "Visualizações",
    "Banco",
    "Configurações",
]

st.set_page_config(
    page_title="Data Senior Analytics",
    page_icon="DA",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
        st.session_state.selected_page = "Resumo"

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
            <p class="hero-subtitle">Painel executivo para diagnóstico, exploração e suporte à decisão.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Ambiente", "Executivo")
    with c2:
        st.metric("Build", get_build_id())
    with c3:
        if df is not None and not df.empty:
            st.metric("Dataset ativo", st.session_state.data_name)
        else:
            st.metric("Dataset ativo", "Sem dados")

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
    st.subheader("Resumo Executivo")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Python", "3.11")
    with c2:
        st.metric("Framework", "Streamlit")
    with c3:
        st.metric("Fonte", "Kaggle")
    with c4:
        st.metric("Tabelas SQLite", len(db.list_tables()))

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Direcionamento</span>', unsafe_allow_html=True)
            st.markdown('<div class="exec-card-title">Objetivo</div>', unsafe_allow_html=True)
            st.write(
                "Transformar dados tabulares em insights acionáveis para decisão rápida e segura."
            )
            st.markdown('<div class="exec-card-title">Valor</div>', unsafe_allow_html=True)
            st.write("Fluxo analítico ponta a ponta com padrão sênior e foco em negócio.")

    with right:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Contexto de dados</span>', unsafe_allow_html=True)
            st.markdown(
                '<div class="exec-card-title">Status dos Dados</div>', unsafe_allow_html=True
            )
            if df is not None and not df.empty:
                st.write(f"Dataset: **{st.session_state.data_name}**")
                st.write(f"Linhas: **{df.shape[0]:,}**")
                st.write(f"Colunas: **{df.shape[1]}**")
                st.write(f"Fonte: **{st.session_state.data_source}**")
            else:
                st.info("Nenhum dataset carregado no momento.")

    s1, s2, s3 = st.columns(3)
    if df is not None and not df.empty:
        null_rate = (df.isna().sum().sum() / max(1, (df.shape[0] * df.shape[1]))) * 100
        dup_rate = (df.duplicated().sum() / max(1, df.shape[0])) * 100
        numeric_cols = df.select_dtypes(include="number").shape[1]
        insight_msg = f"Dataset pronto para exploracao com {numeric_cols} colunas numericas."
        risk_msg = f"Nulos: {null_rate:.2f}% | Duplicadas: {dup_rate:.2f}%."
        action_msg = "Priorizar EDA e, em seguida, consolidar tabela curada no SQLite."
    else:
        insight_msg = "Sem dataset ativo para gerar leitura executiva."
        risk_msg = "Sem risco calculavel sem dados carregados."
        action_msg = "Iniciar pela pagina Upload e validar qualidade minima."

    with s1:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Insight</span>', unsafe_allow_html=True)
            st.write(insight_msg.replace("exploracao", "exploração"))
    with s2:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Risco</span>', unsafe_allow_html=True)
            st.write(risk_msg)
    with s3:
        with st.container(border=True):
            st.markdown('<span class="exec-pill">Ação</span>', unsafe_allow_html=True)
            st.write(action_msg)

    st.markdown("### Diferenciais Profissionais")
    d1, d2 = st.columns(2)
    with d1:
        with st.container(border=True):
            st.markdown("#### Para Recrutadores")
            st.write("- Entrega ponta a ponta: ingestão, EDA, visualização e persistência.")
            st.write("- Comunicação executiva com foco em decisão e valor de negócio.")
            st.write("- Projeto com padrão de qualidade e reprodutibilidade.")
    with d2:
        with st.container(border=True):
            st.markdown("#### Para Liderança Técnica")
            st.write("- Arquitetura modular com responsabilidades claras.")
            st.write("- Quality gates ativos: lint, testes e preflight de deploy.")
            st.write("- Governança de dados explícita com proveniência Kaggle.")

    st.markdown("### Maturidade Analítica")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.caption("Confiabilidade de Dados")
        st.progress(88)
    with m2:
        st.caption("Prontidão para Produção")
        st.progress(90)
    with m3:
        st.caption("Clareza Executiva")
        st.progress(92)


def render_upload(db: SQLiteManager) -> None:
    st.subheader("Upload de Dados")
    uploaded = st.file_uploader("Envie CSV ou Excel", type=["csv", "xlsx", "xls"])

    if uploaded is None:
        st.info("Envie um arquivo para substituir o dataset de demonstração.")
        return

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.session_state.data = df
    st.session_state.data_name = uploaded.name
    st.session_state.data_source = "upload"

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Linhas", f"{df.shape[0]:,}")
    with k2:
        st.metric("Colunas", df.shape[1])
    with k3:
        st.metric("Memória", f"{df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")

    st.success(f"Arquivo carregado com sucesso: {uploaded.name}")
    st.caption("Prévia (primeiras 50 linhas)")
    st.table(df.head(50))

    table_name = st.text_input(
        "Nome da tabela SQLite",
        value=uploaded.name.replace(".", "_"),
        key="upload_table_name",
    )
    if st.button("Salvar no SQLite", key="save_sqlite_button", use_container_width=True):
        ok = db.df_to_sql(df, table_name)
        if ok:
            st.success(f"Tabela salva: {table_name}")
        else:
            st.error("Falha ao salvar no SQLite.")


def render_data_preview(df: pd.DataFrame | None) -> None:
    st.subheader("Visualização dos Dados")
    if df is None or df.empty:
        st.warning("Nenhum dado disponível.")
        return

    tab1, tab2 = st.tabs(["Amostra", "Perfil de Colunas"])

    with tab1:
        st.caption("Prévia (primeiras 200 linhas)")
        st.table(df.head(200))

    with tab2:
        info = pd.DataFrame(
            {
                "Coluna": df.columns,
                "Tipo": df.dtypes.astype(str).values,
                "Nulos": df.isna().sum().values,
                "Únicos": [df[c].nunique(dropna=True) for c in df.columns],
            }
        )
        st.table(info)


def render_eda(df: pd.DataFrame | None) -> None:
    st.subheader("Análise Exploratória")
    if df is None or df.empty:
        st.warning("Nenhum dado disponível.")
        return

    numeric = df.select_dtypes(include="number")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Linhas", f"{len(df):,}")
    with c2:
        st.metric("Valores nulos", int(df.isna().sum().sum()))
    with c3:
        st.metric("Linhas duplicadas", int(df.duplicated().sum()))

    if numeric.empty:
        st.info("Não há colunas numéricas para estatística descritiva.")
        return

    tab_stats, tab_corr = st.tabs(["Estatística", "Correlação"])

    with tab_stats:
        st.table(numeric.describe().T)

    with tab_corr:
        if numeric.shape[1] > 1:
            corr = numeric.corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True, aspect="auto", title="Matriz de Correlação")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("São necessárias ao menos 2 colunas numéricas.")


def render_charts(df: pd.DataFrame | None) -> None:
    st.subheader("Visualizações")
    if df is None or df.empty:
        st.warning("Nenhum dado disponível.")
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if numeric_cols:
        col = st.selectbox("Variável numérica", numeric_cols, key="chart_numeric_variable")
        fig = px.histogram(df, x=col, nbins=30, title=f"Distribuição: {col}")
        st.plotly_chart(fig, use_container_width=True)

    if cat_cols and numeric_cols:
        left, right = st.columns(2)
        with left:
            cat = st.selectbox("Categoria", cat_cols, key="chart_category")
        with right:
            val = st.selectbox(
                "Métrica",
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
        fig = px.bar(grouped.head(15), x=cat, y=val, title=f"Média de {val} por {cat}")
        st.plotly_chart(fig, use_container_width=True)


def render_database(db: SQLiteManager) -> None:
    st.subheader("Banco SQLite")
    tables = db.list_tables()
    if not tables:
        st.info("Nenhuma tabela encontrada no SQLite.")
        return

    table = st.selectbox("Tabela", tables, key="database_table")
    count = db.fetch_scalar(f"SELECT COUNT(*) FROM [{table}]") or 0
    st.metric("Linhas na tabela", int(count))

    preview = db.sql_to_df(f"SELECT * FROM [{table}] LIMIT 500")
    st.caption("Prévia da tabela (até 500 linhas)")
    st.table(preview)


def render_settings(df: pd.DataFrame | None) -> None:
    st.subheader("Configurações e Runtime")
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
    apply_executive_style()
    db = get_db()
    df = st.session_state.data

    render_header(df)
    page = st.radio(
        "Navegação",
        PAGE_OPTIONS,
        horizontal=True,
        key="selected_page",
        label_visibility="collapsed",
    )

    with st.sidebar:
        st.markdown("## Contexto")
        st.caption(f"Build: `{get_build_id()}`")
        st.caption(f"Página: **{page}**")
        if df is not None and not df.empty:
            st.caption(f"Dataset: **{st.session_state.data_name}**")
            st.caption(f"Linhas: {df.shape[0]:,}")
            st.caption(f"Colunas: {df.shape[1]}")
            if st.session_state.data_source == "sample_auto":
                st.info("Dataset padrão carregado automaticamente.")

        if st.button("Resetar sessão", use_container_width=True):
            for key in ("data", "data_name", "data_source"):
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    page_handlers = {
        "Resumo": lambda: render_home(df, db),
        "Upload": lambda: render_upload(db),
        "Dados": lambda: render_data_preview(df),
        "EDA": lambda: render_eda(df),
        "Visualizações": lambda: render_charts(df),
        "Banco": lambda: render_database(db),
        "Configurações": lambda: render_settings(df),
    }

    try:
        page_handlers[page]()
    except Exception as exc:  # noqa: BLE001
        st.error("Falha ao renderizar esta página. O app continua disponível.")
        st.exception(exc)


if __name__ == "__main__":
    main()
