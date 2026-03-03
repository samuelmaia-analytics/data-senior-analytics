"""Renderiza??o da p?gina Home do dashboard."""

import streamlit as st


def render_home_page(db):
    st.header("ðŸ  PÃ¡gina Inicial - Dashboard AnalÃ­tico")

    # MÃ©tricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ðŸ Python", "3.14.2", "Latest")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ðŸ¼ Pandas", "2.2.3", "Stable")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ðŸŽˆ Streamlit", "1.41.1", "Latest")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("ðŸ“Š Plotly", "6.0.0", "Latest")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Cards de informaÃ§Ãµes
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.subheader("ðŸš€ Sobre o Projeto")
        st.markdown("""
        **Dashboard profissional para anÃ¡lise de dados** desenvolvido com as mais recentes tecnologias:

        âœ… **Upload inteligente** - Suporte a CSV/Excel com detecÃ§Ã£o automÃ¡tica de encoding
        âœ… **AnÃ¡lise exploratÃ³ria** - EstatÃ­sticas descritivas, correlaÃ§Ãµes, outliers
        âœ… **VisualizaÃ§Ãµes completas** - 15+ tipos de grÃ¡ficos interativos
        âœ… **SÃ©ries temporais** - TendÃªncias, sazonalidade, previsÃµes
        âœ… **RelatÃ³rios automÃ¡ticos** - GeraÃ§Ã£o de insights e mÃ©tricas
        âœ… **Banco de dados** - SQLite integrado para persistÃªncia
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.subheader("ðŸ“‹ Como Usar")
        st.markdown("""
        1. **ðŸ“¤ Upload de Dados** - Carregue seu arquivo CSV ou Excel
        2. **ðŸ“Š Visualizar** - Explore os dados brutos
        3. **ðŸ“ˆ AnÃ¡lises** - Descubra insights automÃ¡ticos
        4. **ðŸ“Š GrÃ¡ficos** - Crie visualizaÃ§Ãµes interativas
        5. **ðŸ’¾ Banco** - Salve no SQLite para uso futuro

        **Dicas:**
        - Arquivos com acentos funcionam perfeitamente
        - Suporte a encoding automÃ¡tico
        - Limite de 200MB por arquivo
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # EstatÃ­sticas do sistema
    st.subheader("ðŸ“Š EstatÃ­sticas do Sistema")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.session_state.data is not None:
            st.metric("Dados Carregados", "âœ… Sim", st.session_state.data_name[:20] + "..." if len(
                st.session_state.data_name) > 20 else st.session_state.data_name)
        else:
            st.metric("Dados Carregados", "âŒ NÃ£o")

    with col2:
        tables = db.list_tables()
        st.metric("Tabelas no Banco", len(tables))

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

