"""Renderizacao da pagina de Upload do dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.utils.observability import get_structured_logger, new_trace_id, timed_stage

logger = get_structured_logger("dashboard.upload")


def render_upload_page(db, settings):
    st.header("📤 Upload de Dados")

    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.markdown("### ⬆️ Arraste ou selecione um arquivo")

    uploaded_file = st.file_uploader(
        "Escolha um arquivo",
        type=["csv", "xlsx", "xls"],
        help="Formatos suportados: CSV, Excel (.xlsx, .xls)",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("⚙️ Opções avançadas de upload"):
        encoding_option = st.selectbox(
            "Encoding (se CSV)",
            ["auto", "utf-8", "latin-1", "cp1252", "iso-8859-1"],
        )
        sep_option = st.text_input("Separador (se CSV)", ",")
        sheet_option = st.text_input("Planilha (se Excel)", "0")

    if uploaded_file is not None:
        trace_id = new_trace_id()
        logger.info(
            "upload_started",
            extra={
                "trace_id": trace_id,
                "file_name": uploaded_file.name,
                "encoding_option": encoding_option,
            },
        )
        try:
            with st.spinner(f"🔄 Carregando {uploaded_file.name}..."):
                used_encoding = None
                with timed_stage("load_file") as load_timer:
                    if uploaded_file.name.endswith(".csv"):
                        if encoding_option == "auto":
                            encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
                            df = None

                            for enc in encodings:
                                try:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(uploaded_file, encoding=enc, sep=sep_option)
                                    used_encoding = enc
                                    break
                                except UnicodeDecodeError:
                                    continue

                            if df is None:
                                logger.error(
                                    "upload_failed_encoding",
                                    extra={"trace_id": trace_id, "file_name": uploaded_file.name},
                                )
                                st.error("❌ Não foi possível ler o arquivo com nenhum encoding")
                                st.stop()
                        else:
                            df = pd.read_csv(uploaded_file, encoding=encoding_option, sep=sep_option)
                            used_encoding = encoding_option
                    else:
                        if sheet_option.isdigit():
                            df = pd.read_excel(uploaded_file, sheet_name=int(sheet_option))
                        else:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_option)

                st.session_state.data = df
                st.session_state.data_name = uploaded_file.name
                st.session_state.data_source = "upload"

                logger.info(
                    "upload_loaded",
                    extra={
                        "trace_id": trace_id,
                        "rows": int(df.shape[0]),
                        "columns": int(df.shape[1]),
                        "elapsed_ms": round(load_timer.elapsed_ms, 2),
                        "encoding_detected": used_encoding,
                    },
                )

                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
                if used_encoding:
                    st.info(f"📝 Encoding detectado: {used_encoding}")
                st.markdown("</div>", unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Linhas", f"{df.shape[0]:,}")
                with col2:
                    st.metric("Colunas", df.shape[1])
                with col3:
                    st.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
                with col4:
                    st.metric("Duplicatas", df.duplicated().sum())

                st.subheader("🔍 Preview dos Dados (primeiras 100 linhas)")
                st.dataframe(df.head(100), use_container_width=True)

                st.subheader("📋 Informações das Colunas")
                col_info = pd.DataFrame(
                    {
                        "Coluna": df.columns,
                        "Tipo": df.dtypes.astype(str).values,
                        "Não Nulos": df.count().values,
                        "Nulos": df.isnull().sum().values,
                        "Nulos %": (df.isnull().sum().values / len(df) * 100).round(2),
                        "Valores Únicos": [df[col].nunique() for col in df.columns],
                    }
                )
                st.dataframe(col_info, use_container_width=True)

                st.subheader("💾 Salvar no Banco de Dados")
                col1, col2 = st.columns(2)
                with col1:
                    table_name = st.text_input("Nome da tabela:", uploaded_file.name.replace(".", "_"))
                    if st.button("💾 Salvar no SQLite"):
                        if table_name and st.button("Confirmar salvamento", key="confirm_save"):
                            with timed_stage("persist_sqlite") as persist_timer:
                                ok = db.df_to_sql(df, table_name)
                            logger.info(
                                "upload_persist",
                                extra={
                                    "trace_id": trace_id,
                                    "table_name": table_name,
                                    "success": ok,
                                    "elapsed_ms": round(persist_timer.elapsed_ms, 2),
                                },
                            )
                            if ok:
                                st.success(f"✅ Dados salvos na tabela '{table_name}'!")
                            else:
                                st.error("❌ Erro ao salvar no banco")

                with col2:
                    if st.button("📥 Download CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Clique para baixar",
                            data=csv,
                            file_name=f"processado_{uploaded_file.name}",
                            mime="text/csv",
                        )

        except Exception as exc:
            logger.exception(
                "upload_failed",
                extra={"trace_id": trace_id, "file_name": uploaded_file.name, "error": str(exc)},
            )
            st.error(f"❌ Erro ao carregar arquivo: {str(exc)}")
            st.exception(exc)

    else:
        st.info("👆 Faça upload de um arquivo CSV ou Excel para começar")

        raw_files = list(settings.RAW_DATA_DIR.glob("*.csv")) + list(settings.RAW_DATA_DIR.glob("*.xlsx"))

        if raw_files:
            st.subheader("📁 Arquivos disponíveis na pasta raw:")
            for file in raw_files:
                st.text(f"   • {file.name}")
