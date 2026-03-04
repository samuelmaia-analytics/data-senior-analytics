"""Utilitários analíticos compartilhados pelo dashboard."""

import numpy as np
import pandas as pd


def detect_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    """Detecta e categoriza colunas por tipo."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    raw_categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    for col in raw_categorical_cols:
        if col in date_cols:
            continue
        non_null = df[col].dropna()
        if non_null.empty:
            continue
        sample_size = min(len(non_null), 200)
        sample = (
            non_null.sample(n=sample_size, random_state=42)
            if len(non_null) > sample_size
            else non_null
        )
        parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
        if parsed.notna().mean() >= 0.8 and col not in date_cols:
            date_cols.append(col)

    categorical_cols = [c for c in raw_categorical_cols if c not in date_cols]

    id_cols = []
    for col in numeric_cols:
        if df[col].nunique() > len(df) * 0.9:
            id_cols.append(col)

    bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()

    return {
        "numeric": [c for c in numeric_cols if c not in id_cols],
        "categorical": categorical_cols,
        "date": date_cols,
        "id": id_cols,
        "boolean": bool_cols,
        "all_numeric": numeric_cols,
    }


def get_basic_stats(df: pd.DataFrame, col: str) -> dict[str, float | int | None]:
    """Calcula estatísticas básicas para uma coluna numérica."""
    stats_dict: dict[str, float | int | None] = {}
    if col in df.select_dtypes(include=[np.number]).columns:
        stats_dict["Média"] = df[col].mean()
        stats_dict["Mediana"] = df[col].median()
        stats_dict["Moda"] = df[col].mode()[0] if not df[col].mode().empty else None
        stats_dict["Desvio Padrão"] = df[col].std()
        stats_dict["Variância"] = df[col].var()
        stats_dict["Mínimo"] = df[col].min()
        stats_dict["Máximo"] = df[col].max()
        stats_dict["Q1"] = df[col].quantile(0.25)
        stats_dict["Q3"] = df[col].quantile(0.75)
        stats_dict["IQR"] = stats_dict["Q3"] - stats_dict["Q1"]
        stats_dict["Assimetria"] = df[col].skew()
        stats_dict["Curtose"] = df[col].kurtosis()
    return stats_dict


def interpret_correlation(corr: float) -> tuple[str, str]:
    """Interpreta o valor da correlação."""
    if abs(corr) > 0.9:
        return "Muito Forte", "🔥"
    if abs(corr) > 0.7:
        return "Forte", "💪"
    if abs(corr) > 0.5:
        return "Moderada", "👍"
    if abs(corr) > 0.3:
        return "Fraca", "👎"
    return "Muito Fraca", "❌"
