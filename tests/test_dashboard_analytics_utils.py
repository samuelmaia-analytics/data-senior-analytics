import pandas as pd

from dashboard.utils.analytics import (
    build_data_quality_summary,
    build_executive_snapshot,
    build_priority_actions,
    detect_column_types,
    get_basic_stats,
    interpret_correlation,
    summarize_correlation_pairs,
    summarize_transformation_log,
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


def test_build_data_quality_summary_exposes_core_quality_metrics():
    df = pd.DataFrame(
        {
            "id": [1, 2, 2],
            "valor": [10.0, None, None],
            "segmento": ["A", "B", "B"],
        }
    )

    summary = build_data_quality_summary(df)

    assert summary["rows"] == 3
    assert summary["columns"] == 3
    assert summary["missing_count"] == 2
    assert summary["duplicate_count"] == 1
    assert summary["quality_score"] < 100
    assert summary["status"] in {"Excellent", "Good", "Attention", "Critical"}


def test_build_priority_actions_flags_quality_risks():
    actions = build_priority_actions(
        {
            "missing_pct": 10.0,
            "duplicate_pct": 3.0,
            "numeric_columns": 0,
            "rows": 10,
        }
    )

    assert len(actions) == 4
    assert any("null" in action.lower() for action in actions)
    assert any("deduplication" in action.lower() for action in actions)


def test_summarize_transformation_log_generates_readable_messages():
    summary = summarize_transformation_log(
        [
            {
                "operation": "clean_column_names",
                "details": {
                    "original": ["Client ID", "Sale Value"],
                    "new": ["client_id", "sale_value"],
                },
            },
            {
                "operation": "handle_missing_values",
                "details": {"missing_before": 8, "missing_after": 0},
            },
            {"operation": "remove_duplicates", "details": {"removed": 3}},
        ]
    )

    assert any("Column standardization" in item for item in summary)
    assert any("Missing values reduced" in item for item in summary)
    assert any("Duplicate removal" in item for item in summary)


def test_build_executive_snapshot_extracts_business_kpis():
    df = pd.DataFrame(
        {
            "data": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "categoria": ["A", "B", "A"],
            "regiao": ["Sul", "Norte", "Sul"],
            "cliente_id": [101, 102, 101],
            "quantidade": [3, 5, 2],
            "desconto": [0, 10, 5],
            "valor_total": [100.0, 250.0, 200.0],
        }
    )

    snapshot = build_executive_snapshot(df)

    assert snapshot["revenue"] == 550.0
    assert round(float(snapshot["avg_ticket"]), 2) == round(550.0 / 3, 2)
    assert snapshot["unique_clients"] == 2
    assert snapshot["top_category"] == "A"
    assert snapshot["top_region"] == "Sul"
    assert not snapshot["revenue_trend"].empty


def test_summarize_correlation_pairs_returns_sorted_pairs():
    df = pd.DataFrame(
        {
            "sales": [10, 20, 30, 40, 50],
            "margin": [1, 2, 3, 4, 5],
            "discount": [5, 4, 3, 2, 1],
        }
    )

    pairs = summarize_correlation_pairs(df, top_n=2)

    assert len(pairs) == 2
    assert pairs.iloc[0]["strength"] in {"Muito Forte", "Forte", "Moderada", "Fraca"}
    assert abs(float(pairs.iloc[0]["correlation"])) >= abs(float(pairs.iloc[1]["correlation"]))
