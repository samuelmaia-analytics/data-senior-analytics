# config/settings.py
"""
Configurações do projeto Data Senior Analytics
"""

from pathlib import Path


class Settings:
    """Classe de configuração do projeto"""

    # Diretório raiz do projeto
    ROOT_DIR = Path(__file__).parent.parent

    # Diretórios de dados
    DATA_DIR = ROOT_DIR / "data"
    SAMPLE_DATA_DIR = DATA_DIR / "sample"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    EXTERNAL_DATA_DIR = DATA_DIR / "external"

    # Diretórios de saída
    OUTPUTS_DIR = ROOT_DIR / "outputs"
    REPORTS_DIR = OUTPUTS_DIR / "reports"
    FIGURES_DIR = OUTPUTS_DIR / "figures"
    MODELS_DIR = OUTPUTS_DIR / "models"

    # Banco SQLite
    SQLITE_PATH = DATA_DIR / "analytics.db"

    @classmethod
    def create_directories(cls):
        """Cria todos os diretórios necessários se não existirem"""
        directories = [
            cls.SAMPLE_DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.EXTERNAL_DATA_DIR,
            cls.REPORTS_DIR,
            cls.FIGURES_DIR,
            cls.MODELS_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Instância global (opcional)
settings = Settings()

# Criar diretórios ao importar
Settings.create_directories()
