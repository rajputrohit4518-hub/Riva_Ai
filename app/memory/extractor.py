from dataclasses import dataclass

from app.memory.models import Memory
from app.memory.policy import MemoryPolicy


@dataclass(frozen=True)
class MemoryCandidate:
    key: str
    value: str
    category: str = "general"


class MemoryExtractor:
    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self._policy = policy or MemoryPolicy()

    def extract(self, user_input: str) -> list[MemoryCandidate]:
        text = user_input.strip()

        if not text:
            return []

        candidates: list[MemoryCandidate] = []

        prefixes = (
            ("remember that ", "general"),
            ("remember ", "general"),
            ("my name is ", "identity"),
            ("i prefer ", "preference"),
            ("i like ", "preference"),
            ("i love ", "preference"),
        )

        lowered = text.lower()

        for prefix, category in prefixes:
            if lowered.startswith(prefix):
                value = text[len(prefix):].strip()

                if not value:
                    return []

                if prefix.startswith("my name"):
                    key = "name"
                elif prefix.startswith("i prefer"):
                    key = "preference"
                elif prefix.startswith("i like"):
                    key = "likes"
                elif prefix.startswith("i love"):
                    key = "loves"
                else:
                    key = "memory"

                decision = self._policy.evaluate(
                    key=key,
                    value=value,
                    category=category,
                )

                if decision.action.value == "remember":
                    candidates.append(
                        MemoryCandidate(
                            key=key,
                            value=value,
                            category=decision.category.value,
                        )
                    )

                break

        return candidates
