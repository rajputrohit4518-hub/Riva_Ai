import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.memory.models import Memory


class MemoryStore:
    def __init__(
        self,
        database_path: str = "data/riva_memory.db",
    ) -> None:
        self.database_path = database_path
        self._memory_connection: sqlite3.Connection | None = None

        if database_path != ":memory:":
            path = Path(database_path)
            path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        if self.database_path == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(
                    ":memory:"
                )

            return self._memory_connection

        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        connection = self._connect()

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    def save(
        self,
        key: str,
        value: str,
        category: str = "general",
    ) -> Memory:
        now = datetime.now(timezone.utc).isoformat()

        connection = self._connect()

        existing = connection.execute(
            "SELECT created_at FROM memories WHERE key = ?",
            (key,),
        ).fetchone()

        created_at = existing[0] if existing else now

        connection.execute(
            """
            INSERT INTO memories
                (key, value, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                updated_at = excluded.updated_at
            """,
            (key, value, category, created_at, now),
        )

        connection.commit()

        return Memory(
            key=key,
            value=value,
            category=category,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(now),
        )

    def get(self, key: str) -> Memory | None:
        connection = self._connect()

        row = connection.execute(
            """
            SELECT key, value, category, created_at, updated_at
            FROM memories
            WHERE key = ?
            """,
            (key,),
        ).fetchone()

        if row is None:
            return None

        return Memory(
            key=row[0],
            value=row[1],
            category=row[2],
            created_at=datetime.fromisoformat(row[3]),
            updated_at=datetime.fromisoformat(row[4]),
        )

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Memory]:
        query = query.strip().lower()

        if not query:
            return []

        words = [
            word
            for word in query.split()
            if len(word) > 1
        ]

        if not words:
            return []

        connection = self._connect()

        rows = connection.execute(
            """
            SELECT key, value, category, created_at, updated_at
            FROM memories
            ORDER BY updated_at DESC
            """
        ).fetchall()

        memories: list[tuple[int, Memory]] = []

        for row in rows:
            memory = Memory(
                key=row[0],
                value=row[1],
                category=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
            )

            searchable = (
                f"{memory.key} "
                f"{memory.value} "
                f"{memory.category}"
            ).lower()

            score = sum(
                1 for word in words
                if word in searchable
            )

            if score > 0:
                memories.append((score, memory))

        memories.sort(
            key=lambda item: (
                item[0],
                item[1].updated_at,
            ),
            reverse=True,
        )

        return [
            memory
            for _, memory in memories[:limit]
        ]

    def delete(self, key: str) -> bool:
        connection = self._connect()

        cursor = connection.execute(
            "DELETE FROM memories WHERE key = ?",
            (key,),
        )

        connection.commit()

        return cursor.rowcount > 0

    def list_all(self) -> list[Memory]:
        connection = self._connect()

        rows = connection.execute(
            """
            SELECT key, value, category, created_at, updated_at
            FROM memories
            ORDER BY updated_at DESC
            """
        ).fetchall()

        return [
            Memory(
                key=row[0],
                value=row[1],
                category=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
            )
            for row in rows
        ]
