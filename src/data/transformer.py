# src/data/transformer.py
"""
Módulo de transformação e limpeza de dados
"""

import pandas as pd
import numpy as np
from loguru import logger
import re


class DataTransformer:
    """
    Transforma e limpa dados
    """

    def __init__(self):
        self.transformations_log = []
        logger.info("DataTransformer inicializado")

    def clean_column_names(self, df):
        """
        Padroniza nomes das colunas
        """
        df = df.copy()

        def clean_name(name):
            name = str(name).lower().strip()
            name = re.sub(r"[^\w\s]", "", name)
            name = re.sub(r"\s+", "_", name)
            return name

        original_columns = df.columns.tolist()
        df.columns = [clean_name(col) for col in df.columns]

        self._log_transformation(
            "clean_column_names", {"original": original_columns, "new": df.columns.tolist()}
        )

        logger.debug("Nomes de colunas padronizados")
        return df

    def handle_missing_values(self, df, strategy="auto"):
        """
        Trata valores faltantes

        Args:
            df: DataFrame
            strategy: 'auto', 'drop', 'fill_mean', 'fill_median', 'fill_mode'
        """
        df = df.copy()
        missing_before = df.isnull().sum().sum()

        if missing_before == 0:
            logger.info("Nenhum valor faltante encontrado")
            return df

        if strategy == "drop":
            df = df.dropna()
            logger.info(f"Linhas removidas: {missing_before}")

        elif strategy == "fill_mean":
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col].fillna(df[col].mean(), inplace=True)
            logger.info("Valores faltantes preenchidos com média")

        elif strategy == "fill_median":
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col].fillna(df[col].median(), inplace=True)
            logger.info("Valores faltantes preenchidos com mediana")

        elif strategy == "fill_mode":
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col].fillna(
                        df[col].mode()[0] if not df[col].mode().empty else "Unknown", inplace=True
                    )
            logger.info("Valores faltantes preenchidos com moda")

        elif strategy == "auto":
            for col in df.columns:
                if df[col].isnull().sum() > 0:
                    if df[col].dtype in ["int64", "float64"]:
                        df[col].fillna(df[col].median(), inplace=True)
                    else:
                        df[col].fillna(
                            df[col].mode()[0] if not df[col].mode().empty else "Unknown",
                            inplace=True,
                        )
            logger.info("Valores faltantes tratados automaticamente")

        missing_after = df.isnull().sum().sum()
        self._log_transformation(
            "handle_missing_values",
            {"missing_before": missing_before, "missing_after": missing_after},
        )

        return df

    def remove_duplicates(self, df, subset=None):
        """
        Remove linhas duplicadas
        """
        df = df.copy()
        before = len(df)
        df = df.drop_duplicates(subset=subset)
        after = len(df)

        removed = before - after
        if removed > 0:
            logger.info(f"Removidas {removed} linhas duplicadas")

        self._log_transformation(
            "remove_duplicates", {"before": before, "after": after, "removed": removed}
        )

        return df

    def convert_dtypes(self, df):
        """
        Converte tipos de dados automaticamente
        """
        df = df.copy()

        for col in df.columns:
            # Tenta converter para datetime
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                    logger.debug(f"Coluna {col} convertida para datetime")
                    continue
                except:
                    pass

                # Tenta converter para numérico
                try:
                    df[col] = pd.to_numeric(df[col])
                    logger.debug(f"Coluna {col} convertida para numérico")
                except:
                    pass

        self._log_transformation("convert_dtypes", {"dtypes": df.dtypes.to_dict()})

        return df

    def create_features(self, df, date_column=None):
        """
        Cria features adicionais
        """
        df = df.copy()

        if date_column and date_column in df.columns:
            # Garante que é datetime
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column])

            # Cria features de data
            df[f"{date_column}_year"] = df[date_column].dt.year
            df[f"{date_column}_month"] = df[date_column].dt.month
            df[f"{date_column}_day"] = df[date_column].dt.day
            df[f"{date_column}_dayofweek"] = df[date_column].dt.dayofweek
            df[f"{date_column}_quarter"] = df[date_column].dt.quarter

            logger.info(f"Features de data criadas a partir de {date_column}")

        self._log_transformation("create_features", {"new_columns": list(df.columns)})

        return df

    def _log_transformation(self, operation, details):
        """Registra transformação no log interno"""
        self.transformations_log.append({"operation": operation, "details": details})

    def get_transformation_log(self):
        """Retorna log de transformações"""
        return self.transformations_log
