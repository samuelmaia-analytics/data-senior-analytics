"""Renderiza??o da p?gina render_exploratory_page."""

def render_exploratory_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📈 Análise Exploratória de Dados")

    if st.session_state.data is not None:
        df = st.session_state.data

        # Detectar tipos de colunas
        col_types = detect_column_types(df)

        # Resumo geral
        st.subheader("📊 Resumo Geral")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Linhas", f"{df.shape[0]:,}")
        with col2:
            st.metric("Total Colunas", df.shape[1])
        with col3:
            st.metric("Colunas Numéricas", len(col_types['numeric']))
        with col4:
            st.metric("Colunas Categóricas", len(col_types['categorical']))

        # Análise de valores faltantes
        st.subheader("⚠️ Análise de Valores Faltantes")

        missing_df = pd.DataFrame({
            'Coluna': df.columns,
            'Valores Faltantes': df.isnull().sum().values,
            'Percentual': (df.isnull().sum().values / len(df) * 100).round(2)
        }).sort_values('Valores Faltantes', ascending=False)

        # Mostrar apenas colunas com valores faltantes
        missing_with_data = missing_df[missing_df['Valores Faltantes'] > 0]

        if len(missing_with_data) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(missing_with_data, use_container_width=True)
            with col2:
                fig = px.bar(
                    missing_with_data.head(20),
                    x='Coluna',
                    y='Valores Faltantes',
                    title="Top Colunas com Valores Faltantes",
                    color='Valores Faltantes',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ Não há valores faltantes no dataset!")

        # Estatísticas descritivas
        if col_types['numeric']:
            st.subheader("📊 Estatísticas Descritivas - Variáveis Numéricas")
            stats_df = df[col_types['numeric']].describe().T
            # Adicionar skewness e kurtosis
            for col in col_types['numeric']:
                stats_df.loc[col, 'skew'] = df[col].skew()
                stats_df.loc[col, 'kurtosis'] = df[col].kurtosis()
            st.dataframe(stats_df, use_container_width=True)

        # Análise de valores únicos para categóricas
        if col_types['categorical']:
            st.subheader("📝 Análise de Variáveis Categóricas")

            cat_stats = []
            for col in col_types['categorical'][:10]:  # Limitar a 10
                value_counts = df[col].value_counts()
                if len(value_counts) > 0:
                    cat_stats.append({
                        'Coluna': col,
                        'Valores Únicos': df[col].nunique(),
                        'Moda': value_counts.index[0],
                        'Frequência da Moda': value_counts.iloc[0],
                        '% da Moda': round((value_counts.iloc[0] / len(df) * 100), 2)
                    })

            if cat_stats:
                st.dataframe(pd.DataFrame(cat_stats), use_container_width=True)

        # Detecção de outliers
        if col_types['numeric']:
            st.subheader("🔍 Detecção de Outliers (Método IQR)")

            outliers_info = []
            for col in col_types['numeric'][:10]:  # Limitar a 10
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

                outliers_info.append({
                    'Coluna': col,
                    'Outliers': len(outliers),
                    '% Outliers': round((len(outliers) / len(df) * 100), 2),
                    'Limite Inferior': round(lower_bound, 2),
                    'Limite Superior': round(upper_bound, 2)
                })

            outliers_df = pd.DataFrame(outliers_info)
            st.dataframe(outliers_df, use_container_width=True)

        # Insights automáticos
        st.subheader("💡 Insights Automáticos")

        insights = []

        # Tamanho do dataset
        if df.shape[0] > 10000:
            insights.append(f"📊 **Dataset grande**: {df.shape[0]:,} linhas")
        elif df.shape[0] > 1000:
            insights.append(f"📊 **Dataset médio**: {df.shape[0]:,} linhas")
        else:
            insights.append(f"📊 **Dataset pequeno**: {df.shape[0]} linhas")

        # Valores faltantes
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            missing_pct = (missing_total / (df.shape[0] * df.shape[1])) * 100
            insights.append(f"⚠️ **Valores faltantes**: {missing_total} ({missing_pct:.1f}% do total)")
        else:
            insights.append("✅ **Sem valores faltantes**")

        # Duplicatas
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / df.shape[0]) * 100
            insights.append(f"🔄 **Linhas duplicadas**: {duplicates} ({dup_pct:.1f}%)")
        else:
            insights.append("✅ **Sem linhas duplicadas**")

        # Correlações fortes
        if len(col_types['numeric']) > 1:
            corr_matrix = df[col_types['numeric']].corr()
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corr.append(
                            f"{corr_matrix.columns[i]} x {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.2f}")

            if strong_corr:
                insights.append(f"🔗 **Correlações fortes encontradas**: {len(strong_corr)} pares")
                for corr in strong_corr[:3]:  # Mostrar apenas 3
                    insights.append(f"   - {corr}")

        for insight in insights:
            st.markdown(f"- {insight}")

        # Salvar no histórico
        if st.button("💾 Salvar esta análise no histórico"):
            st.session_state.analysis_history.append({
                'timestamp': datetime.now(),
                'data': st.session_state.data_name,
                'insights': insights
            })
            st.success("✅ Análise salva no histórico!")

    else:
        st.warning("⚠️ Nenhum dado carregado. Vá para '📤 Upload de Dados' primeiro.")

    # Página Visualizações Completas
