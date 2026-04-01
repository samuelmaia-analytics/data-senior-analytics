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


def test_sqlite_manager_purges_expired_datasets(tmp_path: Path):
    db_path = tmp_path / "retention.db"
    manager = SQLiteManager(db_path=str(db_path))
    df = pd.DataFrame({"valor_total": [10.0]})

    ok = manager.df_to_sql(
        df,
        "expired_table",
        metadata={
            "retention_days": -1,
            "persistence_mode": "masked",
            "contains_personal_data": False,
            "contains_sensitive_data": False,
            "legal_basis_acknowledged": False,
            "privacy_risk_level": "Minimal",
        },
    )

    assert ok is True
    assert "expired_table" in manager.list_tables()
    assert not manager.get_expiring_datasets(within_days=0).empty

    purged = manager.purge_expired_datasets()

    assert purged == 1
    assert "expired_table" not in manager.list_tables()
    audit_log = manager.get_dataset_audit_log("expired_table")
    assert "purge_expired_dataset" in audit_log["action"].tolist()
