import pandas as pd

from src.data.file_extractor import FileExtractor
from src.data.sqlite_manager import SQLiteManager
from src.data.transformer import DataTransformer


def test_extract_excel_and_json(tmp_path):
    source_df = pd.DataFrame({"id": [1, 2], "segmento": ["A", "B"]})

    excel_path = tmp_path / "dados.xlsx"
    json_path = tmp_path / "dados.json"
    source_df.to_excel(excel_path, index=False)
    source_df.to_json(json_path, orient="records")

    extractor = FileExtractor(data_dir=tmp_path)
    excel_df = extractor.extract_excel("dados.xlsx")
    json_df = extractor.extract_json("dados.json")

    assert excel_df.shape == (2, 2)
    assert json_df.shape == (2, 2)


def test_find_files_and_extract_all_csv(tmp_path):
    pd.DataFrame({"a": [1]}).to_csv(tmp_path / "a.csv", index=False)
    pd.DataFrame({"b": [2]}).to_csv(tmp_path / "b.csv", index=False)

    extractor = FileExtractor(data_dir=tmp_path)
    files = extractor.find_files("*.csv")
    all_csv = extractor.extract_all_csv()

    assert len(files) == 2
    assert sorted(all_csv.keys()) == ["a", "b"]


def test_extract_all_excel_reads_xlsx_and_xls(tmp_path):
    sample = pd.DataFrame({"x": [10, 20]})
    sample.to_excel(tmp_path / "planilha.xlsx", index=False)
    sample.to_excel(tmp_path / "planilha.xls", index=False)

    extractor = FileExtractor(data_dir=tmp_path)
    all_excel = extractor.extract_all_excel()

    assert "planilha" in all_excel
    assert not all_excel["planilha"].empty


def test_transformer_strategies_and_feature_creation():
    transformer = DataTransformer()

    raw = pd.DataFrame(
        {
            "id": [1, 1, 2],
            "valor": [10.0, None, 20.0],
            "categoria": ["A", None, "B"],
            "data_ref": ["2026-01-01", "2026-01-01", "2026-01-03"],
            "numero_txt": ["1", "2", "3"],
        }
    )

    no_missing = transformer.handle_missing_values(pd.DataFrame({"x": [1, 2]}), strategy="auto")
    dropped = transformer.handle_missing_values(raw, strategy="drop")
    filled_mean = transformer.handle_missing_values(raw, strategy="fill_mean")
    filled_median = transformer.handle_missing_values(raw, strategy="fill_median")
    filled_mode = transformer.handle_missing_values(raw, strategy="fill_mode")

    deduped = transformer.remove_duplicates(raw, subset=["id"])
    converted = transformer.convert_dtypes(raw)
    featured = transformer.create_features(converted, date_column="data_ref")

    assert no_missing.isna().sum().sum() == 0
    assert len(dropped) < len(raw)
    assert filled_mean["valor"].isna().sum() == 0
    assert filled_median["valor"].isna().sum() == 0
    assert filled_mode["categoria"].isna().sum() == 0
    assert len(deduped) == 2
    assert pd.api.types.is_numeric_dtype(converted["numero_txt"])
    assert "data_ref_year" in featured.columns
    assert len(transformer.get_transformation_log()) >= 1


def test_sqlite_manager_query_helpers_and_backup(tmp_path):
    db_path = tmp_path / "analytics.db"
    manager = SQLiteManager(db_path=db_path)

    df = pd.DataFrame({"id": [1, 2], "valor": [100.0, 150.0]})
    assert manager.df_to_sql(df, "gold_metrics") is True

    tables = manager.list_tables()
    selected = manager.sql_to_df("SELECT id, valor FROM gold_metrics ORDER BY id")

    assert "gold_metrics" in tables
    assert selected.shape == (2, 2)

    backup_path = manager.backup_database()
    assert backup_path is not None
    assert backup_path.exists()


def test_sqlite_manager_returns_safe_defaults_for_invalid_query(tmp_path):
    manager = SQLiteManager(db_path=tmp_path / "analytics.db")

    result_df = manager.sql_to_df("SELECT * FROM missing_table")
    rows = manager.fetch_all("SELECT * FROM missing_table")
    scalar = manager.fetch_scalar("SELECT total FROM missing_table")

    assert result_df.empty
    assert rows == []
    assert scalar is None
