"""Shared analytics utilities for the dashboard."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

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
        "top_category_share": None,
        "top_region_share": None,
        "revenue_by_category": pd.DataFrame(),
        "revenue_by_region": pd.DataFrame(),
        "revenue_trend": pd.DataFrame(),
        "trend_direction": "Stable",
        "trend_change_pct": None,
        "latest_period": None,
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
        total_revenue = max(float(revenue_by_category["valor_total"].sum()), 1.0)
        revenue_by_category["share_pct"] = (
            revenue_by_category["valor_total"] / total_revenue * 100
        ).round(2)
        snapshot["revenue_by_category"] = revenue_by_category
        if not revenue_by_category.empty:
            snapshot["top_category"] = str(revenue_by_category.iloc[0]["categoria"])
            snapshot["top_category_share"] = float(revenue_by_category.iloc[0]["share_pct"])

    if {"regiao", "valor_total"}.issubset(df.columns):
        revenue_by_region = (
            df.groupby("regiao", dropna=False)["valor_total"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        total_revenue = max(float(revenue_by_region["valor_total"].sum()), 1.0)
        revenue_by_region["share_pct"] = (
            revenue_by_region["valor_total"] / total_revenue * 100
        ).round(2)
        snapshot["revenue_by_region"] = revenue_by_region
        if not revenue_by_region.empty:
            snapshot["top_region"] = str(revenue_by_region.iloc[0]["regiao"])
            snapshot["top_region_share"] = float(revenue_by_region.iloc[0]["share_pct"])

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
            snapshot["latest_period"] = revenue_trend["data"].max().date().isoformat()
            if len(revenue_trend) >= 2:
                last_value = float(revenue_trend.iloc[-1]["valor_total"])
                previous_value = float(revenue_trend.iloc[-2]["valor_total"])
                if previous_value == 0:
                    change_pct = 100.0 if last_value > 0 else 0.0
                else:
                    change_pct = ((last_value - previous_value) / previous_value) * 100
                snapshot["trend_change_pct"] = round(change_pct, 2)
                if change_pct > 1:
                    snapshot["trend_direction"] = "Up"
                elif change_pct < -1:
                    snapshot["trend_direction"] = "Down"

    return snapshot


def build_decision_brief(
    quality_summary: dict[str, float | int | str] | None,
    business_snapshot: dict[str, object] | None,
    priority_actions: list[str] | None = None,
    analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate analytical signals into an executive-style decision memo."""
    if not quality_summary:
        return {
            "headline": "No active dataset",
            "primary_concern": "A decision brief cannot be generated until a dataset is loaded.",
            "recommended_action": "Use the Upload page or load a demo dataset to initialize the workflow.",
            "decision_risk": "High",
            "confidence_label": "Low",
            "drivers": [],
        }

    score = float(quality_summary["quality_score"])
    missing_pct = float(quality_summary["missing_pct"])
    duplicate_pct = float(quality_summary["duplicate_pct"])
    status = str(quality_summary["status"])
    drivers: list[str] = []

    if missing_pct > 5:
        drivers.append(f"Missing data remains at {missing_pct:.1f}% of observed cells.")
    if duplicate_pct > 1:
        drivers.append(f"Duplicate exposure is {duplicate_pct:.1f}% of rows.")

    if business_snapshot:
        top_category = business_snapshot.get("top_category")
        top_category_share = business_snapshot.get("top_category_share")
        top_region = business_snapshot.get("top_region")
        top_region_share = business_snapshot.get("top_region_share")
        trend_direction = business_snapshot.get("trend_direction")
        trend_change_pct = business_snapshot.get("trend_change_pct")

        if top_category and top_category_share is not None:
            drivers.append(
                f"Top category {top_category} represents {float(top_category_share):.1f}% of revenue."
            )
        if top_region and top_region_share is not None:
            drivers.append(
                f"Top region {top_region} represents {float(top_region_share):.1f}% of revenue."
            )
        if trend_change_pct is not None:
            direction = (
                "up" if trend_direction == "Up" else "down" if trend_direction == "Down" else "flat"
            )
            drivers.append(
                f"Latest revenue period moved {direction} by {abs(float(trend_change_pct)):.1f}%."
            )

    if analysis and analysis.get("insights"):
        drivers.append(str(analysis["insights"][0]))

    if status in {"Critical", "Attention"}:
        headline = "Decision quality is constrained by dataset reliability."
        primary_concern = (
            "Governance checks show that the dataset still carries enough quality risk to weaken "
            "high-confidence conclusions."
        )
        decision_risk = "High" if status == "Critical" else "Medium"
        confidence_label = "Low" if status == "Critical" else "Moderate"
    elif business_snapshot and business_snapshot.get("trend_direction") == "Down":
        headline = "Commercial performance needs closer inspection."
        primary_concern = (
            "Revenue momentum softened in the latest visible period, which may require pricing, "
            "mix, or regional execution review."
        )
        decision_risk = "Medium"
        confidence_label = "High"
    else:
        headline = "The dataset is in a usable state for business review."
        primary_concern = (
            "The current workflow has enough quality control to support exploration, performance "
            "review, and persistence."
        )
        decision_risk = "Low"
        confidence_label = "High" if score >= 90 else "Moderate"

    recommended_action = (
        priority_actions[0]
        if priority_actions
        else "Persist the curated output and review concentration, correlation, and trend signals."
    )

    return {
        "headline": headline,
        "primary_concern": primary_concern,
        "recommended_action": recommended_action,
        "decision_risk": decision_risk,
        "confidence_label": confidence_label,
        "drivers": drivers[:4],
    }


def build_governance_snapshot(
    df: pd.DataFrame | None,
    quality_summary: dict[str, float | int | str] | None,
    transform_log: list[dict[str, Any]] | None,
    data_name: str | None,
    data_source: str | None,
    loaded_at: str | None,
) -> dict[str, Any]:
    """Expose operational trust signals for the dashboard surface."""
    source_labels = {
        "sample_auto": "Default demo",
        "sample_manual": "Demo dataset",
        "upload": "User upload",
    }
    quality_status = quality_summary["status"] if quality_summary else "Unavailable"
    score = float(quality_summary["quality_score"]) if quality_summary else 0.0
    trust_label = "High" if score >= 90 else "Moderate" if score >= 75 else "Low"
    release_label = (
        "Ready for review"
        if quality_status in {"Excellent", "Good"}
        else "Use with caution" if quality_status == "Attention" else "Hold for remediation"
    )

    latest_record = None
    if df is not None and not df.empty:
        datetime_columns = df.select_dtypes(
            include=["datetime64[ns]", "datetimetz"]
        ).columns.tolist()
        if "data" in df.columns and "data" not in datetime_columns:
            parsed = pd.to_datetime(df["data"], errors="coerce")
            if parsed.notna().any():
                latest_record = parsed.max()
        elif datetime_columns:
            latest_record = pd.to_datetime(df[datetime_columns[0]], errors="coerce").max()

    return {
        "data_name": data_name or "No dataset",
        "data_source_label": source_labels.get(data_source or "", "Unknown source"),
        "loaded_at": loaded_at,
        "latest_record": (
            latest_record.isoformat(timespec="seconds") if pd.notna(latest_record) else None
        ),
        "trust_label": trust_label,
        "release_label": release_label,
        "quality_status": quality_status,
        "transformation_count": len(transform_log or []),
    }


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
