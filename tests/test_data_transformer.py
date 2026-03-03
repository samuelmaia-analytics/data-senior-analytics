import pandas as pd

from src.data.transformer import DataTransformer


def test_clean_column_names_standardizes_headers():
    transformer = DataTransformer()
    raw = pd.DataFrame({"Nome Cliente": ["A"], "Valor(R$)": [100]})

    cleaned = transformer.clean_column_names(raw)

    assert cleaned.columns.tolist() == ["nome_cliente", "valorr"]


def test_handle_missing_values_auto_fills_numeric_and_categorical():
    transformer = DataTransformer()
    raw = pd.DataFrame(
        {
            "valor": [10.0, None, 30.0],
            "segmento": ["A", None, "A"],
        }
    )

    filled = transformer.handle_missing_values(raw, strategy="auto")

    assert filled["valor"].isna().sum() == 0
    assert filled["segmento"].isna().sum() == 0
    assert filled.loc[1, "segmento"] == "A"
