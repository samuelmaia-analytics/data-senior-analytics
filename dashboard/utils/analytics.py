"""Shared analytics utilities for the dashboard."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "dashboard_policy.json"


@lru_cache(maxsize=1)
def load_dashboard_policy() -> dict[str, object]:
    """Load dashboard scoring policies from versioned config."""
    with POLICY_PATH.open(encoding="utf-8") as policy_file:
        return json.load(policy_file)


def detect_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    """Detect and categorize columns by semantic type."""
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
        parsed = pd.to_datetime(sample, errors="coerce")
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
    """Return descriptive statistics for a numeric column."""
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
    """Interpret correlation strength."""
    if abs(corr) > 0.9:
        return "Muito Forte", "🔥"
    if abs(corr) > 0.7:
        return "Forte", "💪"
    if abs(corr) > 0.5:
        return "Moderada", "👍"
    if abs(corr) > 0.3:
        return "Fraca", "👎"
    return "Muito Fraca", "❌"


def build_data_quality_summary(
    df: pd.DataFrame, policy: dict[str, object] | None = None
) -> dict[str, float | int | str]:
    """Build a decision-ready summary of dataset quality."""
    quality_policy = (policy or load_dashboard_policy())["quality_score"]
    rows, columns = df.shape
    total_cells = max(1, rows * columns)
    missing_count = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    numeric_count = int(df.select_dtypes(include=[np.number]).shape[1])
    categorical_count = int(df.select_dtypes(include=["object", "category"]).shape[1])
    datetime_count = int(df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).shape[1])
    memory_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))

    missing_pct = float((missing_count / total_cells) * 100)
    duplicate_pct = float((duplicate_count / max(1, rows)) * 100)
    completeness_pct = float(100 - missing_pct)

    score = max(
        0.0,
        min(
            100.0,
            100.0
            - (missing_pct * float(quality_policy["missing_weight"]))
            - (duplicate_pct * float(quality_policy["duplicate_weight"]))
            - (float(quality_policy["no_numeric_penalty"]) if numeric_count == 0 else 0.0)
            - (
                float(quality_policy["small_dataset_penalty"])
                if rows < int(quality_policy["small_dataset_threshold"])
                else 0.0
            ),
        ),
    )

    status_thresholds = quality_policy["status_thresholds"]
    if score >= float(status_thresholds["Excellent"]):
        status = "Excellent"
    elif score >= float(status_thresholds["Good"]):
        status = "Good"
    elif score >= float(status_thresholds["Attention"]):
        status = "Attention"
    else:
        status = "Critical"

    return {
        "rows": rows,
        "columns": columns,
        "missing_count": missing_count,
        "missing_pct": missing_pct,
        "duplicate_count": duplicate_count,
        "duplicate_pct": duplicate_pct,
        "numeric_columns": numeric_count,
        "categorical_columns": categorical_count,
        "datetime_columns": datetime_count,
        "memory_mb": memory_mb,
        "completeness_pct": completeness_pct,
        "quality_score": round(score, 2),
        "status": status,
    }


def build_priority_actions(
    summary: dict[str, float | int | str], policy: dict[str, object] | None = None
) -> list[str]:
    """Translate quality metrics into concrete next actions."""
    action_policy = (policy or load_dashboard_policy())["priority_actions"]
    actions: list[str] = []

    if float(summary["missing_pct"]) > float(action_policy["missing_pct_threshold"]):
        actions.append("Prioritize null handling before sharing business-facing insights.")
    if float(summary["duplicate_pct"]) > float(action_policy["duplicate_pct_threshold"]):
        actions.append("Review business keys and deduplication to avoid double counting.")
    if int(summary["numeric_columns"]) == 0:
        actions.append("Add numeric measures to unlock KPI, correlation, and trend analysis.")
    if int(summary["rows"]) < int(action_policy["minimum_rows"]):
        actions.append("Increase sample size before making high-confidence decisions.")
    if not actions:
        actions.append("Dataset is ready for analytical exploration and persistence.")

    return actions


def summarize_transformation_log(log: list[dict]) -> list[str]:
    """Convert the transformation log into UI-ready statements."""
    summary: list[str] = []
    for item in log:
        operation = item.get("operation", "unknown")
        details = item.get("details", {})

        if operation == "clean_column_names":
            original = details.get("original", [])
            new = details.get("new", [])
            renamed = sum(
                1 for old, new_name in zip(original, new, strict=False) if old != new_name
            )
            summary.append(f"Column standardization applied to {renamed} fields.")
        elif operation == "convert_dtypes":
            summary.append("Automatic dtype inference executed for object columns.")
        elif operation == "handle_missing_values":
            before = details.get("missing_before", 0)
            after = details.get("missing_after", 0)
            summary.append(f"Missing values reduced from {before} to {after}.")
        elif operation == "remove_duplicates":
            removed = details.get("removed", 0)
            summary.append(f"Duplicate removal eliminated {removed} rows.")
        elif operation == "create_features":
            summary.append("Feature generation step executed.")

    return summary


def build_business_snapshot(df: pd.DataFrame) -> dict[str, object]:
    """Build a business snapshot from the curated dataset."""
    snapshot: dict[str, object] = {
        "revenue": None,
        "orders": int(len(df)),
        "unique_clients": None,
        "avg_ticket": None,
        "avg_discount": None,
        "items_sold": None,
        "top_category": None,
        "top_region": None,
        "revenue_by_category": pd.DataFrame(),
        "revenue_by_region": pd.DataFrame(),
        "revenue_trend": pd.DataFrame(),
    }

    if "valor_total" in df.columns:
        snapshot["revenue"] = float(df["valor_total"].sum())
        snapshot["avg_ticket"] = float(df["valor_total"].mean())

    if "cliente_id" in df.columns:
        snapshot["unique_clients"] = int(df["cliente_id"].nunique(dropna=True))

    if "desconto" in df.columns:
        snapshot["avg_discount"] = float(df["desconto"].mean())

    if "quantidade" in df.columns:
        snapshot["items_sold"] = float(df["quantidade"].sum())

    if {"categoria", "valor_total"}.issubset(df.columns):
        revenue_by_category = (
            df.groupby("categoria", dropna=False)["valor_total"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        snapshot["revenue_by_category"] = revenue_by_category
        if not revenue_by_category.empty:
            snapshot["top_category"] = str(revenue_by_category.iloc[0]["categoria"])

    if {"regiao", "valor_total"}.issubset(df.columns):
        revenue_by_region = (
            df.groupby("regiao", dropna=False)["valor_total"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        snapshot["revenue_by_region"] = revenue_by_region
        if not revenue_by_region.empty:
            snapshot["top_region"] = str(revenue_by_region.iloc[0]["regiao"])

    if {"data", "valor_total"}.issubset(df.columns):
        date_series = pd.to_datetime(df["data"], errors="coerce")
        trend_df = df.assign(_data=date_series).dropna(subset=["_data"])
        if not trend_df.empty:
            revenue_trend = (
                trend_df.groupby("_data", dropna=False)["valor_total"]
                .sum()
                .reset_index()
                .rename(columns={"_data": "data"})
                .sort_values("data")
            )
            snapshot["revenue_trend"] = revenue_trend

    return snapshot


def summarize_correlation_pairs(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return the strongest correlation pairs for business review."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return pd.DataFrame(columns=["left", "right", "correlation", "strength"])

    corr_matrix = numeric_df.corr(numeric_only=True)
    rows: list[dict[str, object]] = []

    for i, left in enumerate(corr_matrix.columns):
        for j, right in enumerate(corr_matrix.columns):
            if j <= i:
                continue
            corr_value = float(corr_matrix.iloc[i, j])
            strength, _ = interpret_correlation(corr_value)
            rows.append(
                {
                    "left": left,
                    "right": right,
                    "correlation": round(corr_value, 4),
                    "strength": strength,
                }
            )

    if not rows:
        return pd.DataFrame(columns=["left", "right", "correlation", "strength"])

    return (
        pd.DataFrame(rows)
        .assign(abs_correlation=lambda frame: frame["correlation"].abs())
        .sort_values("abs_correlation", ascending=False)
        .drop(columns="abs_correlation")
        .head(top_n)
        .reset_index(drop=True)
    )
