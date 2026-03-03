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
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e6e9f0 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .upload-box {
        border: 3px dashed #FF4B4B;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe9e9 100%);
        transition: all 0.3s;
    }
    .upload-box:hover {
        border-color: #ff6b6b;
        background: linear-gradient(135deg, #ffe9e9 0%, #ffdddd 100%);
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin: 1rem 0;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .correlation-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%);
        border-radius: 15px;
        margin-bottom: 1.5rem;
        color: white;
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


