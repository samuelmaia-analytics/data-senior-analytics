"""Reusable curation workflow shared by UI and tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from dashboard.utils.analytics import (
    build_business_snapshot,
    build_data_quality_summary,
    build_priority_actions,
)
from src.analysis.exploratory import ExploratoryAnalyzer
from src.data.transformer import DataTransformer


@dataclass
class CurationArtifacts:
    raw_df: pd.DataFrame
    curated_df: pd.DataFrame
    analysis: dict[str, Any]
    transform_log: list[dict[str, Any]]
    quality_summary: dict[str, Any]
    priority_actions: list[str]
    business_snapshot: dict[str, Any]


def curate_dataset(df: pd.DataFrame) -> CurationArtifacts:
    """Run the end-to-end curation and profiling pipeline."""
    raw_df = df.copy()
    transformer = DataTransformer()
    curated_df = transformer.clean_column_names(raw_df)
    curated_df = transformer.convert_dtypes(curated_df)
    curated_df = transformer.handle_missing_values(curated_df, strategy="auto")
    curated_df = transformer.remove_duplicates(curated_df)

    analyzer = ExploratoryAnalyzer()
    analysis = analyzer.analyze_dataframe(curated_df, df_name="active_dataset")
    transform_log = transformer.get_transformation_log()
    quality_summary = build_data_quality_summary(curated_df)
    priority_actions = build_priority_actions(quality_summary)
    business_snapshot = build_business_snapshot(curated_df)

    return CurationArtifacts(
        raw_df=raw_df,
        curated_df=curated_df,
        analysis=analysis,
        transform_log=transform_log,
        quality_summary=quality_summary,
        priority_actions=priority_actions,
        business_snapshot=business_snapshot,
    )
