"""
Dashboard Interativo - Data Senior Analytics
Autor: Samuel Maia
Versão: COMPLETA E CORRIGIDA - Todas as páginas funcionando
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.sqlite_manager import SQLiteManager
from config.settings import Settings
from dashboard.pages.home import render_home_page
from dashboard.pages.upload import render_upload_page
from dashboard.pages.data_view import render_data_view_page
from dashboard.pages.exploratory import render_exploratory_page
from dashboard.pages.visualizations import render_visualizations_page
from dashboard.pages.advanced_stats import render_advanced_stats_page
from dashboard.pages.time_series import render_time_series_page
from dashboard.pages.correlations import render_correlations_page
from dashboard.pages.reports import render_reports_page
from dashboard.pages.database import render_database_page
from dashboard.pages.settings_page import render_settings_page
from dashboard.utils.analytics import detect_column_types, get_basic_stats, interpret_correlation

# Tentar importar scipy (opcional)
try:
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None

# Configuração da página (DEVE SER O PRIMEIRO COMANDO)
st.set_page_config(
    page_title="Data Senior Analytics - Samuel Maia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap");

    :root {
        --brand-900: #0f172a;
        --brand-700: #1e293b;
        --brand-500: #334155;
        --accent-600: #d62828;
        --accent-500: #e63946;
        --accent-100: #fdecec;
        --surface-100: #f8fafc;
        --surface-200: #eef2f7;
        --border-200: #dbe3ee;
        --text-900: #111827;
        --text-600: #4b5563;
    }

    .stApp {
        font-family: "Manrope", sans-serif;
        color: var(--text-900);
        background:
            radial-gradient(circle at 20% 0%, #ffffff 0%, #f7f9fc 35%, #eef2f7 100%);
    }

    .stMarkdown p, .stMarkdown li {
        font-size: 0.98rem;
        line-height: 1.55;
        color: var(--text-900);
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 45%, #1f2937 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    .main-header {
        font-family: "Manrope", sans-serif;
        font-size: clamp(2.0rem, 3.4vw, 3.1rem);
        color: var(--brand-900);
        text-align: left;
        margin: 0 0 0.2rem 0;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .sub-header {
        font-size: 1.02rem;
        color: var(--text-600);
        text-align: left;
        margin-bottom: 1.2rem;
        font-weight: 500;
    }

    .metric-card {
        background: linear-gradient(160deg, #ffffff 0%, #f8fafc 65%, #f2f6fb 100%);
        border: 1px solid var(--border-200);
        padding: 1rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #c9d5e5;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
    }

    .upload-box {
        border: 2px dashed #b8c4d6;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        background: linear-gradient(145deg, #ffffff 0%, #f6f9fc 100%);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .upload-box:hover {
        border-color: var(--accent-500);
        box-shadow: 0 8px 30px rgba(214, 40, 40, 0.12);
    }

    .info-box,
    .warning-box,
    .success-box,
    .correlation-card,
    .chart-container {
        border-radius: 14px;
        border: 1px solid var(--border-200);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .info-box {
        background: #f5f9ff;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff8f1;
        border-left: 5px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
    }

    .success-box {
        background: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 1rem;
        margin: 1rem 0;
    }

    .chart-container {
        background: #ffffff;
        padding: 1rem;
        margin: 1rem 0;
    }

    .correlation-card {
        background: #ffffff;
        border-left: 5px solid var(--accent-500);
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .sidebar-header {
        text-align: center;
        padding: 1.2rem;
        background: linear-gradient(160deg, #ef4444 0%, #dc2626 60%, #b91c1c 100%);
        border-radius: 14px;
        margin-bottom: 1.2rem;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.28);
        box-shadow: 0 14px 26px rgba(0, 0, 0, 0.22);
    }

    .stDataFrame,
    [data-testid="stMetric"] {
        border-radius: 12px;
    }

    .metric-card:empty, .info-box:empty, .upload-box:empty, .success-box:empty {
        display: none !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        border: 1px solid #c7d2e3;
        background: #ffffff;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--accent-500);
        color: var(--accent-600);
    }

    @media (max-width: 960px) {
        .main .block-container {
            padding-top: 0.8rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-header,
        .sub-header {
            text-align: left;
        }

        .upload-box {
            padding: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="main-header">📊 Data Senior Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Samuel Maia - Analista de Dados Sênior | Python 3.14 | Streamlit 1.41</p>',
            unsafe_allow_html=True)
st.markdown("---")

# Inicializa session state para armazenar dados
if 'data' not in st.session_state:
    st.session_state.data = None
if 'data_name' not in st.session_state:
    st.session_state.data_name = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []


# Inicializa conexão com banco
@st.cache_resource
def init_db():
    return SQLiteManager()


db = init_db()

# Sidebar
with st.sidebar:
    # Logo em texto (sem imagens externas)
    st.markdown("""
    <div class='sidebar-header'>
        <h1 style='margin:0; font-size:3rem;'>📊📈</h1>
        <h2 style='margin:0.5rem 0 0 0; color:white;'>Data Senior</h2>
        <h3 style='margin:0; color:white; opacity:0.9;'>Analytics</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 👨‍💻 Samuel Maia")
    st.markdown("**Analista de Dados Sênior**")
    st.markdown("📧 smaia2@gmail.com")
    st.markdown("🔗 linkedin.com/in/samuelmaia-data-analyst")
    st.markdown("🐙 https://github.com/samuelmaia-data-analyst/data-senior-analytics")
    st.markdown("---")

    # Navegação
    st.markdown("### 🧭 Navegação")
    page = st.radio(
        "Ir para:",
        ["🏠 Home",
         "📤 Upload de Dados",
         "📊 Visualizar Dados",
         "📈 Análise Exploratória",
         "📊 Visualizações Completas",
         "🔍 Análise Estatística Avançada",
         "📉 Séries Temporais",
         "📊 Correlações e Relacionamentos",
         "📋 Relatórios Automáticos",
         "💾 Banco de Dados",
         "⚙️ Configurações"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Informações dos dados atuais
    if st.session_state.data is not None:
        st.markdown("### 📁 Dados Atuais")
        with st.container():
            st.markdown(f"**Arquivo:** {st.session_state.data_name[:30]}..." if len(
                st.session_state.data_name) > 30 else f"**Arquivo:** {st.session_state.data_name}")
            st.markdown(f"**Linhas:** {st.session_state.data.shape[0]:,}")
            st.markdown(f"**Colunas:** {st.session_state.data.shape[1]}")
            st.markdown(f"**Memória:** {st.session_state.data.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
    else:
        st.info("👆 **Dica:** Faça upload de um arquivo na página '📤 Upload de Dados'")


page_context = {
    "st": st,
    "pd": pd,
    "np": np,
    "px": px,
    "go": go,
    "datetime": datetime,
    "db": db,
    "settings": Settings,
    "scipy_available": SCIPY_AVAILABLE,
    "stats": stats,
    "detect_column_types": detect_column_types,
    "get_basic_stats": get_basic_stats,
    "interpret_correlation": interpret_correlation,
}

if page == "🏠 Home":
    render_home_page(db)

elif page == "📤 Upload de Dados":
    render_upload_page(db, Settings)

elif page == "📊 Visualizar Dados":
    render_data_view_page(**page_context)

elif page == "📈 Análise Exploratória":
    render_exploratory_page(**page_context)

elif page == "📊 Visualizações Completas":
    render_visualizations_page(**page_context)

elif page == "🔍 Análise Estatística Avançada":
    render_advanced_stats_page(**page_context)

elif page == "📉 Séries Temporais":
    render_time_series_page(**page_context)

elif page == "📊 Correlações e Relacionamentos":
    render_correlations_page(**page_context)

elif page == "📋 Relatórios Automáticos":
    render_reports_page(**page_context)

elif page == "💾 Banco de Dados":
    render_database_page(**page_context)

elif page == "⚙️ Configurações":
    render_settings_page(**page_context)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;'>
        <p style='font-size: 1.1rem; font-weight: bold;'>Desenvolvido por <span style='color: #FF4B4B;'>Samuel Maia</span> - Analista de Dados Sênior</p>
        <p style='font-size: 0.9rem; color: #555;'>
            📧 smaia2@gmail.com | 
            🔗 linkedin.com/in/samuelmaia-data-analyst | 
            🐙 github.com/samuelmaia-data-analyst/portfolio-analista-dados
        </p>
        <p style='font-size: 0.8rem; color: #888;'>Python 3.14.2 | Streamlit 1.41.1 | Pandas 2.2.3 | Plotly 6.0.0</p>
        <p style='font-size: 0.8rem; color: #888;'>© 2025 - Todos os direitos reservados</p>
    </div>
    """,
    unsafe_allow_html=True
)


