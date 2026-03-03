import pandas as pd

from src.analysis.exploratory import ExploratoryAnalyzer
from src.data.file_extractor import FileExtractor
from src.data.sqlite_manager import SQLiteManager
from src.data.transformer import DataTransformer


def test_end_to_end_pipeline_integration(tmp_path):
    raw_path = tmp_path / "vendas.csv"
    source_df = pd.DataFrame(
        {
            "Cliente ID": [1, 2, 3, 4],
            "Segmento": ["A", "A", "B", "B"],
            "Valor": [1200.0, 1350.0, 890.0, 940.0],
        }
    )
    source_df.to_csv(raw_path, index=False)

    extractor = FileExtractor(data_dir=tmp_path)
    transformer = DataTransformer()
    analyzer = ExploratoryAnalyzer()
    manager = SQLiteManager(db_path=tmp_path / "analytics.db")

    extracted = extractor.extract_csv("vendas.csv")
    assert not extracted.empty

    cleaned = transformer.clean_column_names(extracted)
    cleaned = transformer.handle_missing_values(cleaned, strategy="auto")
    cleaned = transformer.remove_duplicates(cleaned)

    analysis = analyzer.analyze_dataframe(cleaned, df_name="vendas")
    assert "basic_info" in analysis
    assert analysis["basic_info"]["shape"]["rows"] == 4

    assert manager.df_to_sql(cleaned, "vendas") is True
    persisted_count = manager.fetch_scalar("SELECT COUNT(*) FROM vendas")
    assert persisted_count == 4
