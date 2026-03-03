import pandas as pd

from src.data.file_extractor import FileExtractor


def test_extract_csv_reads_file(tmp_path):
    csv_path = tmp_path / "dados.csv"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(csv_path, index=False)

    extractor = FileExtractor(data_dir=tmp_path)
    df = extractor.extract_csv("dados.csv")

    assert not df.empty
    assert df.shape == (2, 2)


def test_extract_csv_returns_empty_for_invalid_path(tmp_path):
    extractor = FileExtractor(data_dir=tmp_path)
    df = extractor.extract_csv("inexistente.csv")

    assert isinstance(df, pd.DataFrame)
    assert df.empty
