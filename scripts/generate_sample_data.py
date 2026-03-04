# scripts/generate_sample_data.py
"""
Gera dados de exemplo para teste
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import logging

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.sqlite_manager import SQLiteManager
from config.settings import Settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_sales_data(n_records=1000):
    """
    Gera dados de vendas fictícios

    Args:
        n_records: Número de registros a gerar

    Returns:
        DataFrame com dados de vendas
    """
    np.random.seed(42)  # Para resultados reproduzíveis

    produtos = ["Notebook", "Mouse", "Teclado", "Monitor", "Cadeira"]
    regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
    categorias = ["Eletrônicos", "Periféricos", "Móveis"]

    datas = pd.date_range(start="2024-01-01", end="2024-12-31", periods=n_records)

    data = {
        "data": datas,
        "produto": np.random.choice(produtos, n_records),
        "categoria": np.random.choice(categorias, n_records),
        "regiao": np.random.choice(regioes, n_records),
        "quantidade": np.random.randint(1, 50, n_records),
        "preco_unitario": np.random.uniform(50, 5000, n_records).round(2),
        "desconto": np.random.choice([0, 5, 10, 15, 20], n_records, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        "cliente_id": np.random.randint(1000, 9999, n_records),
    }

    df = pd.DataFrame(data)

    # Calcular valor total
    df["valor_total"] = (
        df["quantidade"] * df["preco_unitario"] * (1 - df["desconto"] / 100)
    ).round(2)

    # Adicionar algumas colunas derivadas
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name()

    return df


def generate_customer_data(n_records=500):
    """
    Gera dados de clientes fictícios

    Args:
        n_records: Número de registros a gerar

    Returns:
        DataFrame com dados de clientes
    """
    np.random.seed(42)

    nomes = ["João", "Maria", "José", "Ana", "Carlos", "Mariana", "Pedro", "Juliana"]
    sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Ferreira", "Lima"]
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", "Fortaleza"]
    estados = ["SP", "RJ", "MG", "DF", "BA", "CE"]
    segmentos = ["Varejo", "Atacado", "Corporativo"]

    data = {
        "cliente_id": np.arange(1000, 1000 + n_records),
        "nome": np.random.choice(nomes, n_records) + " " + np.random.choice(sobrenomes, n_records),
        "cidade": np.random.choice(cidades, n_records),
        "estado": np.random.choice(estados, n_records),
        "segmento": np.random.choice(segmentos, n_records),
        "data_cadastro": pd.date_range(start="2020-01-01", end="2024-12-31", periods=n_records),
        "ativo": np.random.choice([True, False], n_records, p=[0.85, 0.15]),
        "score": np.random.randint(0, 100, n_records),
        "limite_credito": np.random.uniform(1000, 50000, n_records).round(2),
    }

    return pd.DataFrame(data)


def main():
    """Função principal"""
    logger.info("=" * 50)
    logger.info("GERADOR DE DADOS DE EXEMPLO")
    logger.info("=" * 50)

    # Inicializa componentes
    db = SQLiteManager()

    # Gera dados de vendas
    logger.info("\n📊 Gerando dados de vendas...")
    sales_df = generate_sales_data(5000)
    logger.info(f"   {len(sales_df):,} registros de vendas gerados")
    logger.info(f"   Colunas: {list(sales_df.columns)}")

    # Salva no SQLite
    logger.info("\n💾 Salvando no SQLite...")
    db.df_to_sql(sales_df, "vendas")

    # Gera dados de clientes
    logger.info("\n👥 Gerando dados de clientes...")
    customers_df = generate_customer_data(1000)
    logger.info(f"   {len(customers_df):,} clientes gerados")

    # Salva no SQLite
    db.df_to_sql(customers_df, "clientes")

    # Salva como CSV
    logger.info("\n📁 Salvando arquivos CSV...")
    Settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    sales_path = Settings.RAW_DATA_DIR / "vendas_exemplo.csv"
    sales_df.to_csv(sales_path, index=False)
    logger.info(f"   Vendas salvo em: {sales_path}")

    customers_path = Settings.RAW_DATA_DIR / "clientes_exemplo.csv"
    customers_df.to_csv(customers_path, index=False)
    logger.info(f"   Clientes salvo em: {customers_path}")

    # Lista tabelas no banco
    logger.info("\n📋 Tabelas no SQLite:")
    tables = db.list_tables()
    for table in tables:
        count = db.fetch_scalar(f"SELECT COUNT(*) FROM {table}")
        if count is not None:
            logger.info(f"   - {table}: {int(count):,} registros")

    logger.info("\n" + "=" * 50)
    logger.info("✅ Dados gerados com sucesso!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
