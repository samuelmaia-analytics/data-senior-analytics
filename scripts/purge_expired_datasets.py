"""Purge expired SQLite datasets based on registered retention metadata."""

from __future__ import annotations

from src.data.sqlite_manager import SQLiteManager


def main() -> int:
    manager = SQLiteManager()
    purged = manager.purge_expired_datasets()
    print(f"Expired datasets purged: {purged}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
