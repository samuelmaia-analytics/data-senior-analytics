from pathlib import Path

import pandas as pd

from src.data.sqlite_manager import SQLiteManager


def test_sqlite_manager_registers_persistence_metadata(tmp_path: Path):
    db_path = tmp_path / "governance.db"
    manager = SQLiteManager(db_path=str(db_path))
    df = pd.DataFrame({"valor_total": [10.0, 20.0], "email": ["a@example.com", "b@example.com"]})

    ok = manager.df_to_sql(
        df,
        "sales_masked",
        metadata={
            "retention_days": 30,
            "persistence_mode": "masked",
            "contains_personal_data": True,
            "contains_sensitive_data": False,
            "legal_basis_acknowledged": True,
            "privacy_risk_level": "Medium",
            "source_name": "sales.csv",
            "data_source": "upload",
            "personal_columns": ["email"],
            "sensitive_columns": [],
        },
    )

    assert ok is True

    registry = manager.get_dataset_registry()
    audit_log = manager.get_dataset_audit_log("sales_masked")

    assert "sales_masked" in registry["table_name"].tolist()
    assert registry.iloc[0]["persistence_mode"] == "masked"
    assert int(registry.iloc[0]["contains_personal_data"]) == 1
    assert not audit_log.empty
    assert audit_log.iloc[0]["action"] == "persist_dataset"
