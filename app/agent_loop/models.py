from dataclasses import dataclass
from enum import Enum


class DecisionType(str, Enum):
    RESPOND = "respond"
    USE_TOOL = "use_tool"
    MEMORY = "memory"


@dataclass(frozen=True)
class AgentDecision:
    decision_type: DecisionType
    tool_name: str | None = None
    tool_arguments: dict | None = None
    response: str | None = None
    memory_action: str | None = None
    memory_key: str | None = None
    memory_value: str | None = None
