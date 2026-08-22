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

        if category == "general":
            category = self._infer_category(
                key,
                value,
            )

        decision = self._policy.evaluate(
            key=key,
            value=value,
            category=category,
        )

        if decision.action == MemoryAction.IGNORE:
            raise ValueError(
                f"Memory rejected: {decision.reason}"
            )

        category = (
            decision.category.value
            if hasattr(decision.category, "value")
            else str(decision.category)
        )

        return self._store.save(
            key=key,
            value=value,
            category=category,
        )

    def _infer_category(
        self,
        key: str,
        value: str,
    ) -> str:
        normalized_key = key.strip().lower()

        if normalized_key in {
            "name",
            "age",
            "location",
            "city",
            "country",
        }:
            return "identity"

        if (
            normalized_key.startswith("favorite ")
            or normalized_key.startswith("favourite ")
            or "preference" in normalized_key
            or normalized_key.startswith("like ")
            or normalized_key.startswith("dislike ")
        ):
            return "preference"

        return "general"

    def recall(self, key: str) -> Memory | None:
        return self._store.get(key.strip())

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Memory]:
        if query is None:
            return []

        if not isinstance(query, str):
            return []

        query = " ".join(query.strip().lower().split())

        if not query:
            return []

        if not isinstance(limit, int) or isinstance(limit, bool):
            return []

        if limit <= 0:
            return []

        if limit > 1000:
            limit = 1000

        if not isinstance(query, str) or not query.strip():
            return []

        if not query:
            return []

        return self._store.search(
            query=query,
            limit=limit,
        )

    def forget(self, key: str) -> bool:
        return self._store.delete(key.strip())

    def list_memories(self) -> list[Memory]:
        return self._store.list_all()
