"""Renderização da página Home do dashboard."""

import streamlit as st


def render_home_page(db):
    st.header("🏠 Página Inicial - Dashboard Analítico")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🐍 Python", "3.14.2", "Latest")
    with col2:
        st.metric("🐼 Pandas", "2.2.3", "Stable")
    with col3:
        st.metric("🎈 Streamlit", "1.41.1", "Latest")
    with col4:
        st.metric("📊 Plotly", "6.0.0", "Latest")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Sobre o Projeto")
        st.markdown(
            """
        **Dashboard profissional para análise de dados** desenvolvido com as mais recentes tecnologias:

        ✅ **Upload inteligente** - Suporte a CSV/Excel com detecção automática de encoding
        ✅ **Análise exploratória** - Estatísticas descritivas, correlações, outliers
        ✅ **Visualizações completas** - 15+ tipos de gráficos interativos
        ✅ **Séries temporais** - Tendências, sazonalidade, previsões
        ✅ **Relatórios automáticos** - Geração de insights e métricas
        ✅ **Banco de dados** - SQLite integrado para persistência
        """
        )

    with col2:
        st.subheader("📋 Como Usar")
        st.markdown(
            """
        1. **📤 Upload de Dados** - Carregue seu arquivo CSV ou Excel
        2. **📊 Visualizar** - Explore os dados brutos
        3. **📈 Análises** - Descubra insights automáticos
        4. **📊 Gráficos** - Crie visualizações interativas
        5. **💾 Banco** - Salve no SQLite para uso futuro

        **Dicas:**
        - Arquivos com acentos funcionam perfeitamente
        - Suporte a encoding automático
        - Limite de 200MB por arquivo
        """
        )

    st.markdown("---")
    st.subheader("📊 Estatísticas do Sistema")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.session_state.data is not None:
            file_label = (
                st.session_state.data_name[:20] + "..."
                if len(st.session_state.data_name) > 20
                else st.session_state.data_name
            )
            st.metric("Dados Carregados", "✅ Sim", file_label)
        else:
            st.metric("Dados Carregados", "❌ Não")

    with col2:
        st.metric("Tabelas no Banco", len(db.list_tables()))

    with col3:
        if st.session_state.data is not None:
            st.metric("Linhas", f"{st.session_state.data.shape[0]:,}")
        else:
            st.metric("Linhas", "0")

    with col4:
        if st.session_state.data is not None:
            st.metric("Colunas", st.session_state.data.shape[1])
        else:
            st.metric("Colunas", "0")
