# src/data/file_extractor.py
"""
Extrator de dados de arquivos locais
"""

import pandas as pd
from pathlib import Path
import logging
import glob
from config.settings import Settings

# Configurar logger
logger = logging.getLogger(__name__)


class FileExtractor:
    """Extrai dados de arquivos locais"""

    def __init__(self, data_dir=None):
        """
        Inicializa o extrator com um diretório de dados

        Args:
            data_dir: Caminho para o diretório de dados (opcional)
        """
        self.data_dir = Path(data_dir) if data_dir else Settings.RAW_DATA_DIR
        logger.info(f"FileExtractor inicializado: {self.data_dir}")

    def extract_csv(self, file_path, **kwargs):
        """
        Extrai dados de arquivo CSV

        Args:
            file_path: Caminho do arquivo CSV
            **kwargs: Argumentos adicionais do pandas.read_csv

        Returns:
            DataFrame com os dados
        """
        try:
            path = Path(file_path)
            if not path.exists():
                path = self.data_dir / file_path

            logger.info(f"Lendo CSV: {path}")
            df = pd.read_csv(path, **kwargs)
            logger.info(f"Arquivo lido: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler CSV {file_path}: {e}")
            return pd.DataFrame()

    def extract_excel(self, file_path, sheet_name=0, **kwargs):
        """
        Extrai dados de arquivo Excel

        Args:
            file_path: Caminho do arquivo Excel
            sheet_name: Nome ou índice da planilha
            **kwargs: Argumentos adicionais do pandas.read_excel

        Returns:
            DataFrame com os dados
        """
        try:
            path = Path(file_path)
            if not path.exists():
                path = self.data_dir / file_path

            logger.info(f"Lendo Excel: {path}, sheet: {sheet_name}")
            df = pd.read_excel(path, sheet_name=sheet_name, **kwargs)
            logger.info(f"Arquivo lido: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler Excel {file_path}: {e}")
            return pd.DataFrame()

    def extract_json(self, file_path, **kwargs):
        """
        Extrai dados de arquivo JSON

        Args:
            file_path: Caminho do arquivo JSON
            **kwargs: Argumentos adicionais do pandas.read_json

        Returns:
            DataFrame com os dados
        """
        try:
            path = Path(file_path)
            if not path.exists():
                path = self.data_dir / file_path

            logger.info(f"Lendo JSON: {path}")
            df = pd.read_json(path, **kwargs)
            logger.info(f"Arquivo lido: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler JSON {file_path}: {e}")
            return pd.DataFrame()

    def find_files(self, pattern):
        """
        Encontra arquivos por padrão de busca

        Args:
            pattern: Padrão de busca (ex: "*.csv", "dados_*.xlsx")

        Returns:
            Lista de caminhos dos arquivos encontrados
        """
        search_path = self.data_dir / pattern
        files = glob.glob(str(search_path))
        logger.info(f"Arquivos encontrados com padrão '{pattern}': {len(files)}")
        return files

    def extract_all_csv(self):
        """
        Extrai todos os arquivos CSV do diretório

        Returns:
            Dicionário com nome do arquivo: DataFrame
        """
        csv_files = self.find_files("*.csv")
        dataframes = {}

        for csv_file in csv_files:
            name = Path(csv_file).stem
            dataframes[name] = self.extract_csv(csv_file)

        logger.info(f"Extraídos {len(dataframes)} arquivos CSV")
        return dataframes

    def extract_all_excel(self):
        """
        Extrai todos os arquivos Excel do diretório

        Returns:
            Dicionário com nome do arquivo: DataFrame
        """
        excel_files = self.find_files("*.xlsx") + self.find_files("*.xls")
        dataframes = {}

        for excel_file in excel_files:
            name = Path(excel_file).stem
            dataframes[name] = self.extract_excel(excel_file)

        logger.info(f"Extraídos {len(dataframes)} arquivos Excel")
        return dataframes
