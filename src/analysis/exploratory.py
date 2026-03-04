# src/analysis/exploratory.py
"""
Análise exploratória de dados automatizada
"""

import pandas as pd
import numpy as np
from loguru import logger
import json
from datetime import datetime


class ExploratoryAnalyzer:
    """
    Realiza análise exploratória completa
    """

    def __init__(self):
        self.results = {}
        logger.info("ExploratoryAnalyzer inicializado")

    def analyze_dataframe(self, df, df_name="dataset"):
        """
        Análise completa do DataFrame

        Args:
            df: DataFrame para análise
            df_name: Nome do dataset

        Returns:
            Dicionário com resultados
        """
        logger.info(f"Iniciando análise de {df_name}")

        analysis = {
            "basic_info": self._basic_info(df),
            "data_types": self._data_types(df),
            "missing_values": self._missing_values(df),
            "descriptive_stats": self._descriptive_stats(df),
            "unique_values": self._unique_values(df),
            "insights": self._generate_insights(df),
        }

        self.results[df_name] = analysis
        logger.success(f"Análise concluída para {df_name}")

        return analysis

    def _basic_info(self, df):
        """Informações básicas"""
        return {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB",
            "columns": list(df.columns),
        }

    def _data_types(self, df):
        """Tipos de dados"""
        dtypes = df.dtypes.value_counts()
        return {
            "summary": {str(k): int(v) for k, v in dtypes.items()},
            "details": df.dtypes.astype(str).to_dict(),
        }

    def _missing_values(self, df):
        """Valores faltantes"""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100

        missing_df = pd.DataFrame({"count": missing, "percentage": missing_pct}).sort_values(
            "count", ascending=False
        )

        return {
            "total_missing": int(df.isnull().sum().sum()),
            "total_missing_pct": float(
                (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            ),
            "columns_with_missing": int((missing > 0).sum()),
            "details": missing_df[missing_df["count"] > 0].to_dict(),
        }

    def _descriptive_stats(self, df):
        """Estatísticas descritivas"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return {"message": "Sem colunas numéricas"}

        stats = df[numeric_cols].describe(percentiles=[0.25, 0.5, 0.75]).to_dict()

        # Adiciona skewness e kurtosis
        for col in numeric_cols:
            if col not in stats:
                stats[col] = {}
            stats[col]["skewness"] = float(df[col].skew())
            stats[col]["kurtosis"] = float(df[col].kurtosis())

        return stats

    def _unique_values(self, df):
        """Valores únicos por coluna"""
        unique_info = {}

        for col in df.columns:
            n_unique = df[col].nunique()
            unique_info[col] = {
                "n_unique": int(n_unique),
                "unique_ratio": float(n_unique / len(df)),
                "sample": df[col].dropna().unique()[:5].tolist() if n_unique <= 10 else [],
            }

        return unique_info

    def _generate_insights(self, df):
        """Gera insights automáticos"""
        insights = []

        # Insight 1: Tamanho do dataset
        if df.shape[0] > 10000:
            insights.append(f"📊 Dataset grande: {df.shape[0]:,} linhas")
        elif df.shape[0] > 1000:
            insights.append(f"📊 Dataset médio: {df.shape[0]:,} linhas")
        else:
            insights.append(f"📊 Dataset pequeno: {df.shape[0]} linhas")

        # Insight 2: Valores faltantes
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            missing_pct = (missing_total / (df.shape[0] * df.shape[1])) * 100
            insights.append(f"⚠️ {missing_pct:.1f}% dos valores são faltantes")
        else:
            insights.append("✅ Sem valores faltantes")

        # Insight 3: Colunas numéricas vs categóricas
        numeric = len(df.select_dtypes(include=[np.number]).columns)
        categorical = len(df.select_dtypes(include=["object"]).columns)
        insights.append(f"📐 {numeric} colunas numéricas, {categorical} categóricas")

        # Insight 4: Duplicatas
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / df.shape[0]) * 100
            insights.append(f"🔄 {duplicates} linhas duplicadas ({dup_pct:.1f}%)")

        # Insight 5: Correlações fortes
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] > 1:
            corr_matrix = numeric_df.corr()
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corr.append(f"{corr_matrix.columns[i]} x {corr_matrix.columns[j]}")

            if strong_corr:
                insights.append(f"🔗 Correlações fortes: {', '.join(strong_corr[:3])}")

        return insights

    def save_report(self, df_name, format="json"):
        """
        Salva relatório em arquivo
        """
        if df_name not in self.results:
            logger.error(f"Análise não encontrada para {df_name}")
            return None

        from config.settings import Settings

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            file_path = Settings.REPORTS_DIR / f"analysis_{df_name}_{timestamp}.json"
            with open(file_path, "w") as f:
                json.dump(self.results[df_name], f, indent=4, default=str)

        elif format == "txt":
            file_path = Settings.REPORTS_DIR / f"analysis_{df_name}_{timestamp}.txt"
            with open(file_path, "w") as f:
                f.write(f"RELATÓRIO DE ANÁLISE - {df_name}\n")
                f.write("=" * 50 + "\n\n")

                for key, value in self.results[df_name].items():
                    f.write(f"{key.upper()}:\n")
                    f.write(f"{json.dumps(value, indent=2, default=str)}\n\n")

        logger.success(f"Relatório salvo: {file_path}")
        return file_path
