import pandas as pd

from src.app.curation_service import curate_dataset


def test_curate_dataset_returns_curated_artifacts():
    raw_df = pd.DataFrame(
        {
            "Data Venda": ["2025-01-01", "2025-01-02", "2025-01-02"],
            "Categoria": ["A", "B", "B"],
            "Regiao": ["Sul", "Norte", "Norte"],
            "Cliente ID": [10, 11, 11],
            "Valor Total": [100.0, 250.0, 250.0],
            "Quantidade": [1, 2, 2],
            "Desconto": [0, 5, 5],
        }
    )

    artifacts = curate_dataset(raw_df)

    assert artifacts.raw_df.shape[0] == 3
    assert artifacts.curated_df.shape[0] == 2
    assert "valor_total" in artifacts.curated_df.columns
    assert artifacts.quality_summary["quality_score"] <= 100
    assert artifacts.business_snapshot["revenue"] == 350.0
    assert len(artifacts.priority_actions) >= 1
