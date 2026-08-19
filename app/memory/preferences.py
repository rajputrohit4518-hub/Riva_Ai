from dataclasses import dataclass

from app.memory.models import Memory
from app.memory.policy import MemoryCategory
from app.memory.manager import MemoryManager


@dataclass(frozen=True)
class Preference:
    key: str
    value: str


class PreferenceManager:
    def __init__(self, memory_manager: MemoryManager | None = None) -> None:
        self._memory = memory_manager or MemoryManager()

    def set(self, key: str, value: str) -> Memory:
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Preference key cannot be empty.")

        if not value:
            raise ValueError("Preference value cannot be empty.")

        return self._memory.remember(
            key=f"preference:{key}",
            value=value,
            category=MemoryCategory.PREFERENCE.value,
        )

    def get(self, key: str) -> Preference | None:
        key = key.strip()

        if not key:
            return None

        memory = self._memory.recall(f"preference:{key}")

        if memory is None:
            return None

        return Preference(
            key=key,
            value=memory.value,
        )

    def list(self) -> list[Preference]:
        return [
            Preference(
                key=memory.key.removeprefix("preference:"),
                value=memory.value,
            )
            for memory in self._memory.list_memories()
            if memory.category == MemoryCategory.PREFERENCE.value
            and memory.key.startswith("preference:")
        ]

    def forget(self, key: str) -> bool:
        key = key.strip()

        if not key:
            return False

        return self._memory.forget(f"preference:{key}")
