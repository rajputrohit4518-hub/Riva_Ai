from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    executor: Callable[..., str]
    category: str = "general"
    risk_level: str = "low"
    requires_confirmation: bool = False

    @property
    def handler(self) -> Callable[..., str]:
        """Backward-compatible alias for executor."""
        return self.executor
