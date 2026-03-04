# scripts/automation.py
"""
Script de automação local - Alternativa gratuita ao AWS Lambda
Executa tarefas agendadas
"""

import schedule
import time
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from src.data.sqlite_manager import SQLiteManager
from src.analysis.exploratory import ExploratoryAnalyzer
from config.settings import Settings


class TaskAutomation:
    """
    Automatiza tarefas localmente
    """

    def __init__(self):
        self.db = SQLiteManager()
        self.analyzer = ExploratoryAnalyzer()
        logger.add("logs/automation.log", rotation="10 MB")

    def daily_report(self):
        """Gera relatório diário"""
        logger.info("📊 Iniciando geração de relatório diário")

        tables = self.db.list_tables()

        report_lines = [
            "=" * 60,
            f"RELATÓRIO DIÁRIO - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "=" * 60,
            "",
        ]

        for table in tables:
            df = self.db.sql_to_df(f"SELECT * FROM {table} LIMIT 100")
            report_lines.append(f"📋 Tabela: {table}")
            report_lines.append(f"   Registros: {len(df)}")
            report_lines.append(f"   Colunas: {list(df.columns)}")
            report_lines.append("")

        # Salva relatório
        report_path = Settings.REPORTS_DIR / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))

        logger.success(f"Relatório salvo: {report_path}")

    def weekly_backup(self):
        """Backup semanal do banco"""
        logger.info("💾 Iniciando backup semanal")
        backup_path = self.db.backup_database()
        if backup_path:
            logger.success(f"Backup concluído: {backup_path}")

    def clean_old_files(self):
        """Remove arquivos antigos"""
        logger.info("🧹 Iniciando limpeza de arquivos antigos")

        from datetime import timedelta

        # Remove backups com mais de 30 dias
        backup_dir = Settings.DATA_DIR / "backups"
        if backup_dir.exists():
            cutoff = datetime.now() - timedelta(days=30)
            for backup in backup_dir.glob("*.db"):
                try:
                    file_date = datetime.strptime(backup.stem.split("_")[-2], "%Y%m%d")
                    if file_date < cutoff:
                        backup.unlink()
                        logger.info(f"Backup removido: {backup}")
                except:
                    pass

        # Remove relatórios com mais de 7 dias
        if Settings.REPORTS_DIR.exists():
            cutoff = datetime.now() - timedelta(days=7)
            for report in Settings.REPORTS_DIR.glob("*.txt"):
                try:
                    file_date = datetime.strptime(report.stem.split("_")[-1], "%Y%m%d")
                    if file_date < cutoff:
                        report.unlink()
                        logger.info(f"Relatório removido: {report}")
                except:
                    pass

    def run(self):
        """Configura e executa agendamentos"""

        # Agenda tarefas
        schedule.every().day.at("18:00").do(self.daily_report)
        schedule.every().monday.at("02:00").do(self.weekly_backup)
        schedule.every().sunday.at("03:00").do(self.clean_old_files)

        logger.info("🚀 Automações iniciadas")
        logger.info("Agendamentos:")
        logger.info("  - Relatório diário: 18:00")
        logger.info("  - Backup semanal: segunda 02:00")
        logger.info("  - Limpeza: domingo 03:00")

        # Executa uma vez imediatamente
        self.daily_report()

        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto


if __name__ == "__main__":
    automation = TaskAutomation()
    automation.run()
