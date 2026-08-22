from dataclasses import dataclass
from enum import Enum


class MemoryAction(str, Enum):
    REMEMBER = "remember"
    IGNORE = "ignore"


class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    FACT = "fact"
    PROJECT = "project"
    ROUTINE = "routine"
    IDENTITY = "identity"
    PROGRAMMING = "programming"
    GENERAL = "general"


@dataclass(frozen=True)
class MemoryDecision:
    action: MemoryAction
    category: str
    reason: str


class MemoryPolicy:
    def evaluate(
        self,
        key: str,
        value: str,
        category: str = "general",
    ) -> MemoryDecision:

        key = key.strip()
        value = value.strip()

        if not key or not value:
            return MemoryDecision(
                action=MemoryAction.IGNORE,
                category=MemoryCategory.GENERAL,
                reason="Empty memory data.",
            )

        try:
            resolved_category = MemoryCategory(category)
        except ValueError:
            resolved_category = MemoryCategory.GENERAL

        return MemoryDecision(
            action=MemoryAction.REMEMBER,
            category=resolved_category,
            reason="Explicit memory request.",
        )

