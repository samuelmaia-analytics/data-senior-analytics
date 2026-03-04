import pandas as pd

from src.data.transformer import DataTransformer

REQUIRED_GOLD_COLUMNS = ["metric_name", "metric_value", "segment", "reference_date"]


def build_gold_output(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["segmento", "data_ref"], as_index=False)["valor"]
        .sum()
        .rename(
            columns={"segmento": "segment", "data_ref": "reference_date", "valor": "metric_value"}
        )
    )
    grouped["metric_name"] = "total_valor"
    return grouped[["metric_name", "metric_value", "segment", "reference_date"]]


def test_gold_output_contract_schema_and_quality_rules():
    source = pd.DataFrame(
        {
            "Segmento": ["A", "A", "B", "B"],
            "Valor": [100.0, 150.0, 200.0, 50.0],
            "Data Ref": ["2026-01-01", "2026-01-01", "2026-01-01", "2026-01-02"],
        }
    )

    transformer = DataTransformer()
    silver = transformer.clean_column_names(source)
    silver = transformer.convert_dtypes(silver)
    gold = build_gold_output(silver)

    assert gold.shape[0] > 0
    assert list(gold.columns) == REQUIRED_GOLD_COLUMNS

    assert gold["metric_name"].notna().all()
    assert gold["segment"].notna().all()
    assert gold["reference_date"].notna().all()
    assert gold["metric_value"].notna().all()
    assert pd.api.types.is_numeric_dtype(gold["metric_value"])

    duplicate_keys = gold.duplicated(subset=["metric_name", "segment", "reference_date"]).sum()
    assert duplicate_keys == 0

    assert gold["metric_value"].map(pd.notna).all()
    assert (~gold["metric_value"].isin([float("inf"), float("-inf")])).all()
