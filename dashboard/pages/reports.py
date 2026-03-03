"""Renderiza??o da p?gina render_reports_page."""

def render_reports_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📋 Relatórios Automáticos")

    if st.session_state.data is not None:
        df = st.session_state.data

        st.subheader("📊 Resumo Executivo")

        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Registros", f"{df.shape[0]:,}")
        with col2:
            st.metric("Total Colunas", df.shape[1])
        with col3:
            st.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
        with col4:
            completude = (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            st.metric("Completude", f"{completude:.1f}%")

        # Top 5 maiores correlações
        col_types = detect_column_types(df)
        if len(col_types['numeric']) > 1:
            st.subheader("🔗 Principais Correlações")
            corr = df[col_types['numeric']].corr().unstack().reset_index()
            corr.columns = ['Var1', 'Var2', 'Correlação']
            corr = corr[corr['Var1'] != corr['Var2']]
            corr['Abs'] = abs(corr['Correlação'])
            corr = corr.sort_values('Abs', ascending=False).drop_duplicates(subset=['Correlação']).head(10)

            st.dataframe(corr[['Var1', 'Var2', 'Correlação']], use_container_width=True)

        # Top categorias
        if col_types['categorical']:
            st.subheader("📝 Top Categorias")
            for col in col_types['categorical'][:3]:
                top = df[col].value_counts().head(5)
                st.write(f"**{col}:**")
                st.dataframe(top.reset_index(), use_container_width=True)

        # Botão para gerar relatório
        if st.button("📥 Gerar Relatório Completo"):
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("RELATÓRIO DE ANÁLISE DE DADOS")
            report_lines.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report_lines.append(f"Arquivo: {st.session_state.data_name}")
            report_lines.append("=" * 60)
            report_lines.append("")
            report_lines.append("RESUMO GERAL")
            report_lines.append("-" * 40)
            report_lines.append(f"Linhas: {df.shape[0]:,}")
            report_lines.append(f"Colunas: {df.shape[1]}")
            report_lines.append(f"Memória: {df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
            report_lines.append(f"Completude: {completude:.1f}%")

            report = "\n".join(report_lines)

            st.download_button(
                label="📥 Download Relatório",
                data=report,
                file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ Nenhum dado carregado")

    # Página Banco de Dados
