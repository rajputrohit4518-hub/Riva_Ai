import sqlite3
from pathlib import Path
from typing import List, Tuple

class ProductionMigrationManager:
    """Manages lightweight version-controlled schema migrations for Riva production SQLite databases."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_migration_table()

    def _init_migration_table(self) -> None:
        """Ensures the schema_migrations tracking table exists."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            conn.commit()
        finally:
            conn.close()

    def get_applied_versions(self) -> List[int]:
        """Returns a list of already applied migration versions."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version ASC")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def apply_migration(self, version: int, name: str, sql_statements: List[str]) -> bool:
        """Applies a versioned migration if not already applied."""
        applied = self.get_applied_versions()
        if version in applied:
            return False

        conn = sqlite3.connect(self.db_path)
        try:
            for stmt in sql_statements:
                conn.execute(stmt)
            conn.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (version, name)
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
