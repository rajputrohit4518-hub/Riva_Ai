from dataclasses import dataclass
from enum import Enum


class DecisionType(str, Enum):
    RESPOND = "respond"
    USE_TOOL = "use_tool"


@dataclass(frozen=True)
class AgentDecision:
    decision_type: DecisionType
    tool_name: str | None = None
    tool_arguments: dict | None = None
    response: str | None = None
