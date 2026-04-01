"""SQLite persistence manager with governance metadata and audit logging."""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from config.settings import Settings

logger = logging.getLogger(__name__)


class SQLiteManager:
    """Manage SQLite reads, writes, and dataset governance metadata."""

    SYSTEM_TABLES = {"dataset_registry", "dataset_audit_log", "sqlite_sequence"}

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or Settings.SQLITE_PATH
        self.conn: sqlite3.Connection | None = None
        logger.info(f"SQLiteManager inicializado: {self.db_path}")

    def connect(self) -> sqlite3.Connection | None:
        """Open a connection and ensure governance tables exist."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self._ensure_system_tables(self.conn)
            return self.conn
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro na conexão: {exc}")
            return None

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def df_to_sql(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "replace",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Persist a DataFrame and register its governance metadata."""
        conn = self.connect()
        if not conn:
            return False

        try:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            self._register_dataset(conn, table_name, df, metadata or {})
            logger.info(f"DataFrame salvo em '{table_name}' ({len(df)} linhas)")
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro ao salvar: {exc}")
            return False
        finally:
            self.disconnect()

    def sql_to_df(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:
        """Execute a SQL query and return a DataFrame."""
        conn = self.connect()
        if not conn:
            return pd.DataFrame()

        try:
            df = pd.read_sql_query(query, conn, params=params)
            logger.debug(f"Query retornou {len(df)} linhas")
            return df
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro na query: {exc}")
            return pd.DataFrame()
        finally:
            self.disconnect()

    def list_tables(self) -> list[str]:
        """List user-facing tables only."""
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        conn = self.connect()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(query)
            tables = [row[0] for row in cursor.fetchall() if row[0] not in self.SYSTEM_TABLES]
            return tables
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro ao listar tabelas: {exc}")
            return []
        finally:
            self.disconnect()

    def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> int | None:
        """Execute a non-SELECT query."""
        conn = self.connect()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro na query: {exc}")
            return None
        finally:
            self.disconnect()

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[tuple[Any, ...]]:
        """Execute a SQL query and return all rows."""
        conn = self.connect()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro na query de leitura: {exc}")
            return []
        finally:
            self.disconnect()

    def fetch_scalar(self, query: str, params: tuple[Any, ...] | None = None) -> Any:
        rows = self.fetch_all(query, params=params)
        if not rows:
            return None
        first_row = rows[0]
        if not first_row:
            return None
        return first_row[0]

    def backup_database(self):
        """Create a timestamped SQLite backup."""
        backup_dir = Settings.DATA_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"analytics_backup_{timestamp}.db"

        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
            return backup_path
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro no backup: {exc}")
            return None

    def get_dataset_registry(self) -> pd.DataFrame:
        return self.sql_to_df("""
            SELECT
                table_name,
                persisted_at,
                retention_until,
                retention_days,
                persistence_mode,
                contains_personal_data,
                contains_sensitive_data,
                legal_basis_acknowledged,
                privacy_risk_level,
                row_count,
                column_count
            FROM dataset_registry
            ORDER BY persisted_at DESC
            """)

    def get_dataset_audit_log(self, table_name: str | None = None) -> pd.DataFrame:
        if table_name:
            return self.sql_to_df(
                """
                SELECT event_at, table_name, action, metadata_json
                FROM dataset_audit_log
                WHERE table_name = ?
                ORDER BY event_at DESC
                """,
                params=(table_name,),
            )
        return self.sql_to_df("""
            SELECT event_at, table_name, action, metadata_json
            FROM dataset_audit_log
            ORDER BY event_at DESC
            LIMIT 200
            """)

    def get_expiring_datasets(self, within_days: int = 7) -> pd.DataFrame:
        return self.sql_to_df(
            """
            SELECT
                table_name,
                retention_until,
                privacy_risk_level,
                contains_personal_data,
                persistence_mode
            FROM dataset_registry
            WHERE retention_until IS NOT NULL
              AND datetime(retention_until) <= datetime('now', ?)
            ORDER BY retention_until ASC
            """,
            params=(f"+{within_days} days",),
        )

    def purge_expired_datasets(self) -> int:
        conn = self.connect()
        if not conn:
            return 0

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name
                FROM dataset_registry
                WHERE retention_until IS NOT NULL
                  AND datetime(retention_until) <= datetime('now')
                """)
            expired_tables = [row[0] for row in cursor.fetchall()]
            purged = 0

            for table_name in expired_tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                event_at = datetime.now().isoformat(timespec="seconds")
                cursor.execute(
                    """
                    INSERT INTO dataset_audit_log (event_at, table_name, action, metadata_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        event_at,
                        table_name,
                        "purge_expired_dataset",
                        json.dumps({"reason": "retention_expired"}, ensure_ascii=False),
                    ),
                )
                cursor.execute("DELETE FROM dataset_registry WHERE table_name = ?", (table_name,))
                purged += 1

            conn.commit()
            return purged
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Erro ao expurgar datasets expirados: {exc}")
            return 0
        finally:
            self.disconnect()

    def log_export_event(
        self,
        table_name: str,
        export_format: str,
        export_mode: str,
        contains_personal_data: bool,
    ) -> None:
        conn = self.connect()
        if not conn:
            return

        try:
            event_at = datetime.now().isoformat(timespec="seconds")
            conn.execute(
                """
                INSERT INTO dataset_audit_log (event_at, table_name, action, metadata_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event_at,
                    table_name,
                    "export_dataset",
                    json.dumps(
                        {
                            "export_format": export_format,
                            "export_mode": export_mode,
                            "contains_personal_data": contains_personal_data,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            conn.commit()
        finally:
            self.disconnect()

    def _ensure_system_tables(self, conn: sqlite3.Connection) -> None:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dataset_registry (
                table_name TEXT PRIMARY KEY,
                persisted_at TEXT NOT NULL,
                retention_until TEXT,
                retention_days INTEGER,
                persistence_mode TEXT NOT NULL,
                contains_personal_data INTEGER NOT NULL,
                contains_sensitive_data INTEGER NOT NULL,
                legal_basis_acknowledged INTEGER NOT NULL,
                privacy_risk_level TEXT NOT NULL,
                column_count INTEGER NOT NULL,
                row_count INTEGER NOT NULL,
                metadata_json TEXT NOT NULL
            )
            """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dataset_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_at TEXT NOT NULL,
                table_name TEXT NOT NULL,
                action TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            )
            """)

    def _register_dataset(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        df: pd.DataFrame,
        metadata: dict[str, Any],
    ) -> None:
        persisted_at = datetime.now().isoformat(timespec="seconds")
        retention_days = int(metadata.get("retention_days", 90))
        retention_until = (datetime.now() + timedelta(days=retention_days)).isoformat(
            timespec="seconds"
        )
        registry_payload = {
            "source_name": metadata.get("source_name"),
            "data_source": metadata.get("data_source"),
            "personal_columns": metadata.get("personal_columns", []),
            "sensitive_columns": metadata.get("sensitive_columns", []),
        }

        conn.execute(
            """
            INSERT OR REPLACE INTO dataset_registry (
                table_name,
                persisted_at,
                retention_until,
                retention_days,
                persistence_mode,
                contains_personal_data,
                contains_sensitive_data,
                legal_basis_acknowledged,
                privacy_risk_level,
                column_count,
                row_count,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                table_name,
                persisted_at,
                retention_until,
                retention_days,
                str(metadata.get("persistence_mode", "raw_curated")),
                int(bool(metadata.get("contains_personal_data", False))),
                int(bool(metadata.get("contains_sensitive_data", False))),
                int(bool(metadata.get("legal_basis_acknowledged", False))),
                str(metadata.get("privacy_risk_level", "Minimal")),
                int(df.shape[1]),
                int(df.shape[0]),
                json.dumps(registry_payload, ensure_ascii=False),
            ),
        )
        conn.execute(
            """
            INSERT INTO dataset_audit_log (event_at, table_name, action, metadata_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                persisted_at,
                table_name,
                "persist_dataset",
                json.dumps(
                    {
                        "retention_days": retention_days,
                        "persistence_mode": metadata.get("persistence_mode", "raw_curated"),
                        "contains_personal_data": bool(
                            metadata.get("contains_personal_data", False)
                        ),
                        "contains_sensitive_data": bool(
                            metadata.get("contains_sensitive_data", False)
                        ),
                        "legal_basis_acknowledged": bool(
                            metadata.get("legal_basis_acknowledged", False)
                        ),
                    },
                    ensure_ascii=False,
                ),
            ),
        )
        conn.commit()
