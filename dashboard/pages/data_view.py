"""Renderiza??o da p?gina render_data_view_page."""

def render_data_view_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📊 Visualização de Dados")

    if st.session_state.data is not None:
        df = st.session_state.data

        # Opções de visualização
        st.subheader("🔍 Opções de Visualização")

        col1, col2, col3 = st.columns(3)
        with col1:
            n_rows = st.slider("Número de linhas para exibir:", 10, 1000, 100, step=10)
        with col2:
            sort_col = st.selectbox("Ordenar por (opcional)", ["Nenhum"] + df.columns.tolist())
        with col3:
            sort_order = st.radio("Ordem", ["Crescente", "Decrescente"], horizontal=True)

        # Filtrar colunas
        all_cols = df.columns.tolist()
        selected_cols = st.multiselect("Selecionar colunas para exibir", all_cols,
                                       default=all_cols[:min(10, len(all_cols))])

        if selected_cols:
            df_view = df[selected_cols].copy()

            # Ordenar
            if sort_col != "Nenhum":
                ascending = sort_order == "Crescente"
                df_view = df_view.sort_values(sort_col, ascending=ascending)

            # Mostrar dados
            st.subheader("📋 Dados")
            st.dataframe(df_view.head(n_rows), use_container_width=True)

            # Download
            csv = df_view.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"visualizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("⚠️ Nenhum dado carregado. Vá para '📤 Upload de Dados' primeiro.")

    # Página Análise Exploratória
