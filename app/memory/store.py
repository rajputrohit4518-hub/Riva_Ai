import sqlite3
from datetime import datetime, timedelta, timezone
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
        now_dt = datetime.now(timezone.utc)

        connection = self._connect()

        existing = connection.execute(
            "SELECT created_at, updated_at FROM memories WHERE key = ?",
            (key,),
        ).fetchone()

        if existing:
            created_at = existing[0]
            previous_updated_at = datetime.fromisoformat(existing[1])

            # Guarantee that an in-place update is strictly newer even
            # when two saves happen within the same clock resolution.
            if now_dt <= previous_updated_at:
                now_dt = previous_updated_at + timedelta(microseconds=1)

            now = now_dt.isoformat()
        else:
            created_at = now_dt.isoformat()
            now = created_at

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
        query = " ".join(query.strip().lower().split())

        if not query or limit <= 0:
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

        ranked = []

        for row in rows:
            memory = Memory(
                key=row[0],
                value=row[1],
                category=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
            )

            key_text = memory.key.lower()
            value_text = memory.value.lower()
            category_text = memory.category.lower()

            key_matches = sum(
                1 for word in words if word in key_text
            )
            value_matches = sum(
                1 for word in words if word in value_text
            )
            category_matches = sum(
                1 for word in words if word in category_text
            )

            if not (
                key_matches
                or value_matches
                or category_matches
            ):
                continue

            exact_key_match = key_text == query

            updated_preference_value_match = (
                value_matches > 0
                and memory.category.lower() == "preference"
                and memory.updated_at > memory.created_at
            )

            if updated_preference_value_match:
                tier = 2000
                relevance = value_matches

            elif exact_key_match:
                tier = 1000
                relevance = len(words)

            elif key_matches:
                tier = 100
                relevance = key_matches

            elif value_matches:
                tier = 10
                relevance = value_matches

            else:
                tier = 1
                relevance = category_matches

            ranked.append(
                (
                    tier,
                    relevance,
                    memory.updated_at,
                    memory,
                )
            )

        ranked.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2],
                item[3].key.lower(),
                item[3].value.lower(),
            ),
            reverse=True,
        )

        return [
            item[3]
            for item in ranked[:limit]
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


