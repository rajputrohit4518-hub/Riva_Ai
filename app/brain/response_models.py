from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResponseType(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RivaResponse:
    response_type: ResponseType
    message: str
    success: bool
    data: Any = None
    command_id: str | None = None
