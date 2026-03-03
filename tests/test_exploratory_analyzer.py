import pandas as pd

from config.settings import Settings
from src.analysis.exploratory import ExploratoryAnalyzer


def test_analyze_dataframe_returns_expected_sections():
    analyzer = ExploratoryAnalyzer()
    df = pd.DataFrame(
        {
            "valor": [10, 20, 30, 40],
            "categoria": ["A", "A", "B", "B"],
        }
    )

    result = analyzer.analyze_dataframe(df, df_name="amostra")

    for key in [
        "basic_info",
        "data_types",
        "missing_values",
        "descriptive_stats",
        "unique_values",
        "insights",
    ]:
        assert key in result


def test_save_report_json_creates_output_file(tmp_path):
    analyzer = ExploratoryAnalyzer()
    df = pd.DataFrame({"valor": [1, 2, 3]})
    analyzer.analyze_dataframe(df, df_name="financeiro")

    old_reports_dir = Settings.REPORTS_DIR
    Settings.REPORTS_DIR = tmp_path
    try:
        report_path = analyzer.save_report("financeiro", format="json")
    finally:
        Settings.REPORTS_DIR = old_reports_dir

    assert report_path is not None
    assert report_path.exists()
