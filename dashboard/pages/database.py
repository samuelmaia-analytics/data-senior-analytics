"""Renderiza??o da p?gina render_database_page."""

def render_database_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("💾 Banco de Dados SQLite")

    # Listar tabelas
    tables = db.list_tables()

    if tables:
        st.subheader("📋 Tabelas Disponíveis")
        selected_table = st.selectbox("Selecione uma tabela:", tables)

        if selected_table:
            # Carregar dados da tabela
            df = db.sql_to_df(f"SELECT * FROM {selected_table} LIMIT 1000")

            # Mostrar informações
            col1, col2, col3 = st.columns(3)
            with col1:
                count = db.fetch_scalar(f"SELECT COUNT(*) FROM {selected_table}")
                count = int(count) if count is not None else 0
                st.metric("Total Registros", f"{count:,}")
            with col2:
                st.metric("Colunas", df.shape[1])
            with col3:
                st.metric("Visualizando", f"{df.shape[0]:,} registros")

            # Mostrar dados
            st.dataframe(df, use_container_width=True)

            # Botões de ação
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Clique para baixar",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )
            with col2:
                if st.button("🗑️ Limpar tabela", type="primary"):
                    if st.checkbox("Confirmar exclusão de todos os dados?"):
                        db.execute_query(f"DELETE FROM {selected_table}")
                        st.success(f"✅ Tabela {selected_table} limpa!")
                        st.rerun()
    else:
        st.info("ℹ️ Nenhuma tabela encontrada no banco de dados.")

    # Página Configurações
