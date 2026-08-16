from dataclasses import dataclass
from enum import Enum
from typing import Any


class IntentType(str, Enum):
    COMMAND = "command"
    QUERY = "query"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ParsedIntent:
    intent_type: IntentType
    capability_name: str | None
    device_type: str | None
    arguments: dict[str, Any]
    confidence: float
    original_text: str
