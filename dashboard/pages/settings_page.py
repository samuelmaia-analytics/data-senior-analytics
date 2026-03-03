"""Renderiza??o da p?gina render_settings_page."""

def render_settings_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("⚙️ Configurações do Sistema")

    st.subheader("📁 Diretórios do Projeto")
    st.json({
        "data_dir": str(settings.DATA_DIR),
        "raw_data": str(settings.RAW_DATA_DIR),
        "processed_data": str(settings.PROCESSED_DATA_DIR),
        "reports_dir": str(settings.REPORTS_DIR)
    })

    st.subheader("🗄️ Banco de Dados")
    st.write(f"**SQLite Path:** {settings.SQLITE_PATH}")
    if settings.SQLITE_PATH.exists():
        size_mb = settings.SQLITE_PATH.stat().st_size / (1024 * 1024)
        st.write(f"**Tamanho:** {size_mb:.2f} MB")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Criar Backup do Banco"):
            backup_path = db.backup_database()
            if backup_path:
                st.success(f"✅ Backup criado: {backup_path}")

    with col2:
        if st.button("🔄 Resetar Sessão"):
            for key in ['data', 'data_name', 'data_source', 'analysis_history']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'analysis_history' else []
            st.success("✅ Sessão resetada!")
            st.rerun()

    st.subheader("📊 Histórico de Análises")
    if st.session_state.analysis_history:
        for i, analysis in enumerate(st.session_state.analysis_history):
            with st.expander(f"Análise {i + 1}: {analysis['timestamp'].strftime('%d/%m/%Y %H:%M')}"):
                st.write(f"**Arquivo:** {analysis['data']}")
                st.write("**Insights:**")
                for insight in analysis['insights']:
                    st.write(f"- {insight}")
    else:
        st.info("Nenhuma análise salva no histórico")
