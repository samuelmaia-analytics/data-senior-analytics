"""Renderiza??o da p?gina render_time_series_page."""

def render_time_series_page(st, pd, np, px, go, datetime, db, settings, scipy_available, stats, detect_column_types, get_basic_stats, interpret_correlation):
    st.header("📉 Análise de Séries Temporais")

    if st.session_state.data is not None:
        df = st.session_state.data

        # Detectar tipos de colunas
        col_types = detect_column_types(df)

        # EXPLICAÇÃO SOBRE SÉRIES TEMPORAIS
        with st.expander("ℹ️ O que são Séries Temporais?", expanded=False):
            st.markdown("""
            **Séries temporais** são conjuntos de dados organizados em ordem cronológica.

            ### Para usar esta seção:
            1. **Coluna de data**: Deve conter datas (ex: '2024-01-01', '01/01/2024')
            2. **Coluna de valor**: Deve conter números para analisar ao longo do tempo

            ### Exemplos de análise:
            - Tendências de vendas ao longo dos meses
            - Sazonalidade (padrões que se repetem)
            - Médias móveis para suavizar flutuações
            """)

        # Verificar se há colunas de data
        if col_types['date']:
            st.success(f"✅ Encontradas {len(col_types['date'])} colunas de data!")

            # Selecionar coluna de data
            date_col = st.selectbox(
                "📅 Selecione a coluna de data:",
                col_types['date'],
                help="Escolha a coluna que contém as datas para análise temporal"
            )

            # Tentar converter para datetime se necessário
            if date_col not in df.select_dtypes(include=['datetime64']).columns:
                with st.spinner(f"Convertendo '{date_col}' para formato de data..."):
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        st.success("✅ Coluna convertida para formato de data!")
                    except Exception as e:
                        st.error(f"❌ Erro ao converter para data: {e}")

            # Verificar se há valores nulos após conversão
            null_dates = df[date_col].isnull().sum()
            if null_dates > 0:
                st.warning(f"⚠️ {null_dates} valores não puderam ser convertidos para data e serão ignorados.")
                df_time = df.dropna(subset=[date_col]).copy()
            else:
                df_time = df.copy()

            # Ordenar por data
            df_time = df_time.sort_values(date_col)

            # Verificar colunas numéricas
            if col_types['numeric']:
                st.success(f"✅ Encontradas {len(col_types['numeric'])} colunas numéricas!")

                # Selecionar coluna de valor
                value_col = st.selectbox(
                    "📊 Selecione a coluna de valor:",
                    col_types['numeric'],
                    help="Escolha a coluna numérica para analisar ao longo do tempo"
                )

                # Período dos dados
                min_date = df_time[date_col].min()
                max_date = df_time[date_col].max()
                date_range = (max_date - min_date).days

                st.info(
                    f"📅 Período analisado: {min_date.strftime('%d/%m/%Y')} até {max_date.strftime('%d/%m/%Y')} ({date_range} dias)")

                # Tipo de gráfico
                st.subheader("📈 Visualizações Temporais")

                chart_type = st.radio(
                    "Tipo de visualização:",
                    ["📈 Gráfico de Linha", "📊 Gráfico de Área", "📉 Média Móvel", "📅 Agregação por Período",
                     "📊 Sazonalidade"],
                    horizontal=True
                )

                if chart_type == "📈 Gráfico de Linha":
                    fig = px.line(
                        df_time,
                        x=date_col,
                        y=value_col,
                        title=f"{value_col} ao longo do tempo",
                        markers=True
                    )

                    fig.update_layout(
                        xaxis_title="Data",
                        yaxis_title=value_col,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Estatísticas
                    st.subheader("📊 Estatísticas da Série")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Média", f"{df_time[value_col].mean():.2f}")
                    with col2:
                        st.metric("Mediana", f"{df_time[value_col].median():.2f}")
                    with col3:
                        st.metric("Mínimo", f"{df_time[value_col].min():.2f}")
                    with col4:
                        st.metric("Máximo", f"{df_time[value_col].max():.2f}")

                elif chart_type == "📊 Gráfico de Área":
                    fig = px.area(
                        df_time,
                        x=date_col,
                        y=value_col,
                        title=f"{value_col} - Gráfico de Área"
                    )

                    fig.update_layout(
                        xaxis_title="Data",
                        yaxis_title=value_col
                    )

                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "📉 Média Móvel":
                    st.markdown("""
                    **Média Móvel** suaviza flutuações de curto prazo para destacar tendências de longo prazo.
                    """)

                    window = st.slider(
                        "Janela da média móvel (dias/períodos):",
                        min_value=2,
                        max_value=min(60, len(df_time) // 2),
                        value=min(7, len(df_time) // 2)
                    )

                    # Calcular média móvel
                    df_time['media_movel'] = df_time[value_col].rolling(window=window, min_periods=1).mean()

                    # Criar gráfico
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=df_time[date_col],
                        y=df_time[value_col],
                        mode='lines',
                        name='Original',
                        line=dict(color='lightgray', width=1),
                        opacity=0.5
                    ))

                    fig.add_trace(go.Scatter(
                        x=df_time[date_col],
                        y=df_time['media_movel'],
                        mode='lines',
                        name=f'Média Móvel {window} períodos',
                        line=dict(color='#FF4B4B', width=3)
                    ))

                    fig.update_layout(
                        title=f"{value_col} - Média Móvel (janela={window})",
                        xaxis_title="Data",
                        yaxis_title=value_col,
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "📅 Agregação por Período":
                    period = st.selectbox(
                        "Agregar por:",
                        ["Dia", "Semana", "Mês", "Trimestre", "Ano"]
                    )

                    if period == "Dia":
                        df_agg = df_time.groupby(df_time[date_col].dt.date)[value_col].sum().reset_index()
                        df_agg.columns = [date_col, value_col]
                        titulo = f"{value_col} por Dia"
                    elif period == "Semana":
                        df_agg = df_time.groupby(df_time[date_col].dt.isocalendar().week)[value_col].sum().reset_index()
                        df_agg.columns = ['Semana', value_col]
                        titulo = f"{value_col} por Semana"
                    elif period == "Mês":
                        df_agg = df_time.groupby(df_time[date_col].dt.to_period('M'))[value_col].sum().reset_index()
                        df_agg[date_col] = df_agg[date_col].astype(str)
                        titulo = f"{value_col} por Mês"
                    elif period == "Trimestre":
                        df_agg = df_time.groupby(df_time[date_col].dt.to_period('Q'))[value_col].sum().reset_index()
                        df_agg[date_col] = df_agg[date_col].astype(str)
                        titulo = f"{value_col} por Trimestre"
                    else:
                        df_agg = df_time.groupby(df_time[date_col].dt.year)[value_col].sum().reset_index()
                        df_agg.columns = ['Ano', value_col]
                        titulo = f"{value_col} por Ano"

                    fig = px.bar(
                        df_agg,
                        x=df_agg.columns[0],
                        y=value_col,
                        title=titulo,
                        color=value_col,
                        color_continuous_scale='Viridis'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "📊 Sazonalidade":
                    st.markdown("""
                    **Análise de Sazonalidade** identifica padrões que se repetem em determinados períodos.
                    """)

                    df_temp = df_time.copy()
                    df_temp['mês'] = df_temp[date_col].dt.month
                    df_temp['ano'] = df_temp[date_col].dt.year
                    df_temp['dia_semana'] = df_temp[date_col].dt.day_name()

                    meses = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    df_temp['mês_nome'] = df_temp['mês'].map(meses)

                    tab1, tab2 = st.tabs(["📅 Sazonalidade Mensal", "📆 Sazonalidade por Dia da Semana"])

                    with tab1:
                        monthly_avg = df_temp.groupby('mês_nome')[value_col].mean().reset_index()
                        ordem_meses = list(meses.values())
                        monthly_avg['mês_nome'] = pd.Categorical(monthly_avg['mês_nome'], categories=ordem_meses,
                                                                 ordered=True)
                        monthly_avg = monthly_avg.sort_values('mês_nome')

                        fig1 = px.line(
                            monthly_avg,
                            x='mês_nome',
                            y=value_col,
                            title="Sazonalidade Mensal (média por mês)",
                            markers=True
                        )
                        st.plotly_chart(fig1, use_container_width=True)

                    with tab2:
                        dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                        dia_map = dict(zip(dias_semana, dias_pt, strict=True))

                        weekday_avg = df_temp.groupby('dia_semana')[value_col].mean().reset_index()
                        weekday_avg['dia_pt'] = weekday_avg['dia_semana'].map(dia_map)

                        weekday_avg['dia_pt'] = pd.Categorical(weekday_avg['dia_pt'], categories=dias_pt, ordered=True)
                        weekday_avg = weekday_avg.sort_values('dia_pt')

                        fig2 = px.bar(
                            weekday_avg,
                            x='dia_pt',
                            y=value_col,
                            title="Média por Dia da Semana",
                            color=value_col,
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                # Botão para download
                if st.button("📥 Download Dados da Série Temporal"):
                    csv = df_time[[date_col, value_col]].to_csv(index=False)
                    st.download_button(
                        label="Clique para baixar CSV",
                        data=csv,
                        file_name=f"serie_temporal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

            else:
                st.warning("⚠️ Nenhuma coluna numérica encontrada para análise temporal.")
                st.info("Para análise de séries temporais, é necessário ter pelo menos uma coluna numérica.")

        else:
            st.warning("⚠️ Nenhuma coluna de data encontrada no dataset.")

            # Oferecer opção de converter uma coluna
            st.subheader("🔄 Converter coluna para data")

            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            if text_cols:
                st.markdown("Algumas colunas de texto podem conter datas. Tente converter:")

                convert_col = st.selectbox("Selecione uma coluna para tentar converter:", text_cols)

                if st.button("🔄 Tentar converter para data"):
                    try:
                        sample = df[convert_col].dropna().iloc[0] if len(df) > 0 else ""
                        pd.to_datetime(sample)

                        st.success(f"✅ A coluna '{convert_col}' parece conter datas válidas!")
                        st.info(
                            "💡 Para usar esta coluna como data, recarregue o arquivo ou processe os dados antes do upload.")

                    except:
                        st.error(f"❌ A coluna '{convert_col}' não pôde ser convertida para data.")
            else:
                st.info("💡 Não há colunas de texto que possam conter datas.")
    else:
        st.warning("⚠️ Nenhum dado carregado. Vá para '📤 Upload de Dados' primeiro.")

    # Página Correlações e Relacionamentos - COMPLETA!
