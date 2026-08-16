from app.memory.models import Memory
from app.memory.policy import MemoryAction, MemoryPolicy
from app.memory.store import MemoryStore


class MemoryManager:
    def __init__(
        self,
        store: MemoryStore | None = None,
        policy: MemoryPolicy | None = None,
    ) -> None:
        self._store = store or MemoryStore()
        self._policy = policy or MemoryPolicy()

    def remember(
        self,
        key: str,
        value: str,
        category: str = "general",
    ) -> Memory:
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError("Memory key cannot be empty.")

        if not value:
            raise ValueError("Memory value cannot be empty.")

        decision = self._policy.evaluate(
            key=key,
            value=value,
            category=category,
        )

        if decision.action == MemoryAction.IGNORE:
            raise ValueError(
                f"Memory rejected: {decision.reason}"
            )

        return self._store.save(
            key=key,
            value=value,
            category=decision.category.value,
        )

    def recall(self, key: str) -> Memory | None:
        return self._store.get(key.strip())

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Memory]:
        return self._store.search(
            query=query,
            limit=limit,
        )

    def forget(self, key: str) -> bool:
        return self._store.delete(key.strip())

    def list_memories(self) -> list[Memory]:
        return self._store.list_all()
