"""Renderiza??o da p?gina render_correlations_page."""

def render_correlations_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📊 Análise de Correlações e Relacionamentos")

    if st.session_state.data is not None:
        df = st.session_state.data

        # Detectar tipos de colunas
        col_types = detect_column_types(df)

        # Verificar se há colunas numéricas
        if len(col_types['all_numeric']) >= 2:
            st.subheader("📈 Matriz de Correlação")

            # Opções de visualização
            col1, col2 = st.columns([2, 1])

            with col1:
                # Selecionar colunas para correlação
                selected_cols = st.multiselect(
                    "Selecione as colunas para análise de correlação",
                    col_types['all_numeric'],
                    default=col_types['all_numeric'][:min(6, len(col_types['all_numeric']))]
                )

            with col2:
                st.markdown("### ℹ️ Sobre Correlações")
                st.markdown("""
                - **> 0.7**: Forte correlação positiva
                - **< -0.7**: Forte correlação negativa
                - **0.3 a 0.7**: Correlação moderada
                - **< 0.3**: Correlação fraca
                """)

            if len(selected_cols) >= 2:
                # Calcular matriz de correlação
                corr_matrix = df[selected_cols].corr()

                # Heatmap de correlação
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title="Matriz de Correlação",
                    zmin=-1, zmax=1
                )
                st.plotly_chart(fig, use_container_width=True)

                # Tabela de correlações detalhada
                st.subheader("📊 Detalhamento das Correlações")

                # Preparar dados para tabela
                corr_pairs = []
                for i in range(len(selected_cols)):
                    for j in range(i + 1, len(selected_cols)):
                        corr_value = corr_matrix.iloc[i, j]
                        strength, emoji = interpret_correlation(corr_value)
                        direction = "positiva" if corr_value > 0 else "negativa"

                        corr_pairs.append({
                            'Variável 1': selected_cols[i],
                            'Variável 2': selected_cols[j],
                            'Correlação': round(corr_value, 4),
                            'Direção': direction,
                            'Intensidade': strength,
                            'Interpretação': f"{emoji} {strength} {direction}"
                        })

                # Ordenar por valor absoluto da correlação
                corr_df = pd.DataFrame(corr_pairs)
                corr_df['|Correlação|'] = abs(corr_df['Correlação'])
                corr_df = corr_df.sort_values('|Correlação|', ascending=False).drop('|Correlação|', axis=1)

                st.dataframe(corr_df, use_container_width=True)

                # Gráfico de dispersão para pares selecionados
                st.subheader("🔄 Gráfico de Dispersão para Pares Selecionados")

                if len(selected_cols) >= 2:
                    col1 = st.selectbox("Selecione a primeira variável", selected_cols, key='scatter1')
                    col2 = st.selectbox("Selecione a segunda variável", [c for c in selected_cols if c != col1],
                                        key='scatter2')

                    fig = px.scatter(
                        df,
                        x=col1,
                        y=col2,
                        title=f"{col1} x {col2}",
                        opacity=0.6,
                        trendline="ols" if st.checkbox("Adicionar linha de tendência") else None
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Estatísticas da correlação
                    corr_val = df[col1].corr(df[col2])
                    st.info(f"📊 Correlação entre {col1} e {col2}: **{corr_val:.4f}**")
            else:
                st.warning("⚠️ Selecione pelo menos 2 colunas para visualizar correlações")

        elif len(col_types['all_numeric']) == 1:
            st.warning(
                "⚠️ Apenas uma coluna numérica encontrada. São necessárias pelo menos 2 colunas numéricas para análise de correlação.")
            st.info(f"Coluna numérica disponível: {col_types['all_numeric'][0]}")
        else:
            st.warning("⚠️ Nenhuma coluna numérica encontrada no dataset.")
            st.info("Para análise de correlação, carregue dados com colunas numéricas.")

        # Se houver colunas categóricas, mostrar análise de associação
        if col_types['categorical'] and scipy_available:
            st.subheader("📊 Associação entre Variáveis Categóricas")

            if len(col_types['categorical']) >= 2:
                cat1 = st.selectbox("Primeira variável categórica", col_types['categorical'], key='cat1')
                cat2 = st.selectbox("Segunda variável categórica", [c for c in col_types['categorical'] if c != cat1],
                                    key='cat2')

                # Tabela de contingência
                contingency = pd.crosstab(df[cat1], df[cat2])

                st.write("**Tabela de Contingência:**")
                st.dataframe(contingency, use_container_width=True)

                # Teste qui-quadrado
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

                st.write("**Teste Qui-quadrado:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estatística χ²", f"{chi2:.4f}")
                with col2:
                    st.metric("Graus de Liberdade", dof)
                with col3:
                    st.metric("Valor p", f"{p_value:.4f}")

                if p_value < 0.05:
                    st.success(f"✅ Há associação significativa entre {cat1} e {cat2} (p < 0.05)")
                else:
                    st.warning("⚠️ Não há evidência de associação significativa (p >= 0.05)")

            elif scipy_available:
                st.info("💡 Selecione pelo menos 2 colunas categóricas para análise de associação")

        elif col_types['categorical'] and not scipy_available:
            st.info("💡 Instale scipy para análise de associação entre variáveis categóricas: `pip install scipy`")
    else:
        st.warning("⚠️ Nenhum dado carregado. Vá para '📤 Upload de Dados' primeiro.")

    # Página Relatórios Automáticos
