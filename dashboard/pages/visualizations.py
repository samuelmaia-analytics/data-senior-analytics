"""Renderiza??o da p?gina render_visualizations_page."""

def render_visualizations_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📊 Visualizações Completas - 15+ Tipos de Gráficos")

    if st.session_state.data is not None:
        df = st.session_state.data

        # Detectar tipos de colunas
        col_types = detect_column_types(df)

        # Mostrar informações sobre colunas disponíveis
        with st.expander("📋 Colunas disponíveis por tipo", expanded=False):
            tab1, tab2, tab3, tab4 = st.tabs(["🔢 Numéricas", "📝 Categóricas", "📅 Datas", "🆔 IDs"])

            with tab1:
                if col_types['numeric']:
                    for col in col_types['numeric']:
                        st.markdown(f"- {col}")
                else:
                    st.write("Nenhuma coluna numérica encontrada")

            with tab2:
                if col_types['categorical']:
                    for col in col_types['categorical']:
                        st.markdown(f"- {col}")
                else:
                    st.write("Nenhuma coluna categórica encontrada")

            with tab3:
                if col_types['date']:
                    for col in col_types['date']:
                        st.markdown(f"- {col}")
                else:
                    st.write("Nenhuma coluna de data encontrada")

            with tab4:
                if col_types['id']:
                    for col in col_types['id']:
                        st.markdown(f"- {col}")
                else:
                    st.write("Nenhuma coluna ID detectada")

        # Categoria de visualização
        chart_category = st.selectbox(
            "Categoria de Visualização",
            ["📊 Distribuições", "📈 Relacionamentos", "📊 Comparações", "📉 Séries Temporais", "📋 Composições"]
        )

        if chart_category == "📊 Distribuições":
            st.subheader("📊 Gráficos de Distribuição")

            if col_types['numeric']:
                col = st.selectbox("Selecione uma coluna numérica", col_types['numeric'])

                chart_type = st.radio(
                    "Tipo de Gráfico",
                    ["Histograma", "Boxplot", "Violino", "Density Plot"],
                    horizontal=True
                )

                if chart_type == "Histograma":
                    bins = st.slider("Número de bins", 5, 100, 30)
                    fig = px.histogram(df, x=col, nbins=bins, title=f"Histograma - {col}", marginal="box")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Boxplot":
                    fig = px.box(df, y=col, title=f"Boxplot - {col}")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Violino":
                    fig = px.violin(df, y=col, title=f"Violino - {col}", box=True)
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Density Plot":
                    fig = px.density_contour(df, x=col, title=f"Density Plot - {col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Nenhuma coluna numérica disponível para gráficos de distribuição")

        elif chart_category == "📈 Relacionamentos":
            st.subheader("📈 Gráficos de Relacionamento")

            if len(col_types['numeric']) >= 2:
                chart_type = st.radio(
                    "Tipo de Gráfico",
                    ["Dispersão", "Matriz de Dispersão", "Heatmap"],
                    horizontal=True
                )

                if chart_type == "Dispersão":
                    col1 = st.selectbox("Eixo X", col_types['numeric'], key='x_rel')
                    col2 = st.selectbox("Eixo Y", [c for c in col_types['numeric'] if c != col1], key='y_rel')

                    fig = px.scatter(df, x=col1, y=col2, title=f"{col1} x {col2}", opacity=0.6)
                    st.plotly_chart(fig, use_container_width=True)

                    # Correlação
                    corr = df[col1].corr(df[col2])
                    st.info(f"📊 Correlação: {corr:.3f}")

                elif chart_type == "Matriz de Dispersão":
                    selected_cols = st.multiselect("Selecione colunas", col_types['numeric'],
                                                   default=col_types['numeric'][:4])
                    if len(selected_cols) >= 2:
                        fig = px.scatter_matrix(df, dimensions=selected_cols, title="Matriz de Dispersão")
                        st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Heatmap":
                    selected_cols = st.multiselect("Selecione colunas", col_types['numeric'],
                                                   default=col_types['numeric'])
                    if len(selected_cols) >= 2:
                        corr = df[selected_cols].corr()
                        fig = px.imshow(corr, text_auto=True, aspect="auto", title="Matriz de Correlação",
                                        color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ São necessárias pelo menos 2 colunas numéricas para gráficos de relacionamento")

        elif chart_category == "📊 Comparações":
            st.subheader("📊 Gráficos de Comparação")

            if col_types['categorical'] and col_types['numeric']:
                cat_col = st.selectbox("Coluna categórica", col_types['categorical'])
                num_col = st.selectbox("Coluna numérica", col_types['numeric'])

                chart_type = st.radio(
                    "Tipo de Gráfico",
                    ["Barras", "Boxplot por Categoria", "Violino por Categoria"],
                    horizontal=True
                )

                if chart_type == "Barras":
                    # Agregar
                    agg_df = df.groupby(cat_col)[num_col].mean().reset_index().sort_values(num_col,
                                                                                           ascending=False).head(20)
                    fig = px.bar(agg_df, x=cat_col, y=num_col, title=f"Média de {num_col} por {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Boxplot por Categoria":
                    fig = px.box(df, x=cat_col, y=num_col, title=f"Boxplot de {num_col} por {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Violino por Categoria":
                    fig = px.violin(df, x=cat_col, y=num_col, title=f"Violino de {num_col} por {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ São necessárias colunas categóricas e numéricas para gráficos de comparação")

        elif chart_category == "📉 Séries Temporais":
            st.subheader("📉 Gráficos de Séries Temporais")

            if col_types['date']:
                date_col = st.selectbox("Coluna de data", col_types['date'])

                if col_types['numeric']:
                    value_col = st.selectbox("Coluna de valor", col_types['numeric'])

                    chart_type = st.radio(
                        "Tipo de Gráfico",
                        ["Linha", "Área", "Barras", "Média Móvel"],
                        horizontal=True
                    )

                    if chart_type == "Linha":
                        fig = px.line(df.sort_values(date_col), x=date_col, y=value_col,
                                      title=f"{value_col} ao longo do tempo")
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "Área":
                        fig = px.area(df.sort_values(date_col), x=date_col, y=value_col, title=f"{value_col} - Área")
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "Barras":
                        fig = px.bar(df.sort_values(date_col), x=date_col, y=value_col, title=f"{value_col} - Barras")
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "Média Móvel":
                        window = st.slider("Janela da média móvel", 2, 30, 7)
                        df_sorted = df.sort_values(date_col).copy()
                        df_sorted['media_movel'] = df_sorted[value_col].rolling(window=window).mean()

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df_sorted[date_col], y=df_sorted[value_col],
                                                 mode='lines', name='Original', opacity=0.5))
                        fig.add_trace(go.Scatter(x=df_sorted[date_col], y=df_sorted['media_movel'],
                                                 mode='lines', name=f'Média Móvel {window}',
                                                 line=dict(color='red', width=3)))
                        fig.update_layout(title=f"{value_col} - Média Móvel")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Nenhuma coluna numérica disponível")
            else:
                st.warning("⚠️ Nenhuma coluna de data encontrada")

        elif chart_category == "📋 Composições":
            st.subheader("📋 Gráficos de Composição")

            if col_types['categorical']:
                cat_col = st.selectbox("Coluna categórica", col_types['categorical'])

                # Contagens
                value_counts = df[cat_col].value_counts().reset_index()
                value_counts.columns = [cat_col, 'Contagem']
                value_counts = value_counts.head(20)

                chart_type = st.radio(
                    "Tipo de Gráfico",
                    ["Pizza", "Rosca", "Barras"],
                    horizontal=True
                )

                if chart_type == "Pizza":
                    fig = px.pie(value_counts, values='Contagem', names=cat_col, title=f"Distribuição - {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Rosca":
                    fig = px.pie(value_counts, values='Contagem', names=cat_col, title=f"Distribuição - {cat_col}",
                                 hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Barras":
                    fig = px.bar(value_counts, x=cat_col, y='Contagem', title=f"Distribuição - {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Nenhuma coluna categórica disponível")
    else:
        st.warning("⚠️ Nenhum dado carregado. Vá para '📤 Upload de Dados' primeiro.")

    # Página Análise Estatística Avançada
