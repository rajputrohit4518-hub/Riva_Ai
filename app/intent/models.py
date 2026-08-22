from dataclasses import dataclass
from enum import Enum


class IntentType(str, Enum):
    UNKNOWN = "unknown"
    GREETING = "greeting"
    CALCULATION = "calculation"
    MEMORY = "memory"
    CONVERSATION = "conversation"
    TOOL_REQUEST = "tool_request"


@dataclass(frozen=True)
class ParsedIntent:
    intent_type: IntentType
    confidence: float = 1.0
    expression: str | None = None
    tool_name: str | None = None
    memory_key: str | None = None
    memory_value: str | None = None
    memory_action: str | None = None
