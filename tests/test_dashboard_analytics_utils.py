import pandas as pd

from dashboard.utils.analytics import (
    detect_column_types,
    get_basic_stats,
    interpret_correlation,
)


def test_detect_column_types_classifies_numeric_categorical_and_id():
    df = pd.DataFrame(
        {
            "id_cliente": [1, 2, 3, 4],
            "segmento": ["A", "B", "A", "B"],
            "valor": [100.0, 120.0, 100.0, 120.0],
        }
    )

    result = detect_column_types(df)

    assert "id_cliente" in result["id"]
    assert "valor" in result["numeric"]
    assert "segmento" in result["categorical"]


def test_get_basic_stats_returns_expected_keys_for_numeric_column():
    df = pd.DataFrame({"valor": [10, 20, 30, 40, 50]})

    stats = get_basic_stats(df, "valor")

    for key in ["Média", "Mediana", "Desvio Padrão", "Mínimo", "Máximo", "IQR"]:
        assert key in stats


def test_interpret_correlation_maps_strength_and_symbol():
    assert interpret_correlation(0.95)[0] == "Muito Forte"
    assert interpret_correlation(0.6)[0] == "Moderada"
    assert interpret_correlation(0.1)[0] == "Muito Fraca"
