import pandas as pd

from src.data.sqlite_manager import SQLiteManager


def test_sqlite_manager_insert_and_scalar_read(tmp_path):
    db_path = tmp_path / "analytics_test.db"
    manager = SQLiteManager(db_path=db_path)

    df = pd.DataFrame({"id": [1, 2, 3], "valor": [10.0, 20.0, 30.0]})
    assert manager.df_to_sql(df, "vendas") is True

    total = manager.fetch_scalar("SELECT COUNT(*) FROM vendas")
    assert total == 3


def test_sqlite_manager_execute_query_returns_affected_rows(tmp_path):
    db_path = tmp_path / "analytics_test.db"
    manager = SQLiteManager(db_path=db_path)

    assert manager.execute_query("CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT)") == -1
    assert manager.execute_query("INSERT INTO clientes (nome) VALUES (?)", ("Ana",)) == 1

    rows = manager.fetch_all("SELECT nome FROM clientes")
    assert rows == [("Ana",)]
