"""Renderiza??o da p?gina render_advanced_stats_page."""

def render_advanced_stats_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("🔍 Análise Estatística Avançada")

    if not scipy_available:
        st.warning(
            "⚠️ Biblioteca 'scipy' não está instalada. Para usar testes estatísticos, instale com: `pip install scipy`")
        st.info("💡 Enquanto isso, você pode usar as outras funcionalidades do dashboard.")

    if st.session_state.data is not None:
        df = st.session_state.data
        col_types = detect_column_types(df)

        if col_types['numeric'] and scipy_available:
            # Testes estatísticos
            test_type = st.selectbox(
                "Selecione o teste estatístico",
                ["Teste t (comparação de médias)",
                 "ANOVA (análise de variância)",
                 "Correlação de Pearson",
                 "Correlação de Spearman"]
            )

            if test_type == "Teste t (comparação de médias)" and col_types['categorical']:
                cat_col = st.selectbox("Variável categórica (2 grupos)", col_types['categorical'])
                num_col = st.selectbox("Variável numérica", col_types['numeric'])

                groups = df[cat_col].dropna().unique()
                if len(groups) == 2:
                    group1 = df[df[cat_col] == groups[0]][num_col].dropna()
                    group2 = df[df[cat_col] == groups[1]][num_col].dropna()

                    t_stat, p_value = stats.ttest_ind(group1, group2)

                    st.subheader("Resultado do Teste t")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Estatística t", f"{t_stat:.4f}")
                    with col2:
                        st.metric("Valor p", f"{p_value:.4f}")

                    if p_value < 0.05:
                        st.success(f"✅ Há diferença significativa entre {groups[0]} e {groups[1]} (p < 0.05)")
                    else:
                        st.warning("⚠️ Não há diferença significativa (p >= 0.05)")
                else:
                    st.warning("⚠️ A variável categórica deve ter exatamente 2 grupos")

            elif test_type == "ANOVA (análise de variância)" and col_types['categorical']:
                cat_col = st.selectbox("Variável categórica", col_types['categorical'])
                num_col = st.selectbox("Variável numérica", col_types['numeric'])

                groups = []
                for _name, group in df.groupby(cat_col)[num_col]:
                    if len(group.dropna()) > 0:
                        groups.append(group.dropna())

                if len(groups) >= 2:
                    f_stat, p_value = stats.f_oneway(*groups)

                    st.subheader("Resultado da ANOVA")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Estatística F", f"{f_stat:.4f}")
                    with col2:
                        st.metric("Valor p", f"{p_value:.4f}")

                    if p_value < 0.05:
                        st.success("✅ Há diferença significativa entre os grupos (p < 0.05)")
                    else:
                        st.warning("⚠️ Não há diferença significativa (p >= 0.05)")
                else:
                    st.warning("⚠️ A variável categórica precisa ter pelo menos 2 grupos com dados")

            elif test_type in ["Correlação de Pearson", "Correlação de Spearman"] and len(col_types['numeric']) >= 2:
                col1 = st.selectbox("Variável 1", col_types['numeric'])
                col2 = st.selectbox("Variável 2", [c for c in col_types['numeric'] if c != col1])

                if test_type == "Correlação de Pearson":
                    corr, p_value = stats.pearsonr(df[col1].dropna(), df[col2].dropna())
                    test_name = "Pearson"
                else:
                    corr, p_value = stats.spearmanr(df[col1].dropna(), df[col2].dropna())
                    test_name = "Spearman"

                st.subheader(f"Resultado da Correlação de {test_name}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Correlação", f"{corr:.4f}")
                with col2:
                    st.metric("Valor p", f"{p_value:.4f}")

                strength, emoji = interpret_correlation(corr)
                direction = "positiva" if corr > 0 else "negativa"

                st.info(f"{emoji} Correlação {direction} ({strength})")

                if p_value < 0.05:
                    st.success("✅ Correlação estatisticamente significativa (p < 0.05)")
                else:
                    st.warning("⚠️ Correlação não significativa (p >= 0.05)")
        elif not scipy_available:
            st.info("💡 Instale scipy para habilitar testes estatísticos")
        else:
            st.warning("⚠️ São necessárias colunas numéricas para testes estatísticos")
    else:
        st.warning("⚠️ Nenhum dado carregado")

    # Página Séries Temporais - COMPLETA!
