from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class PermissionLevel(str, Enum):
    NONE = "none"
    CONFIRM = "confirm"
    ELEVATED = "elevated"


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    permission: PermissionLevel
    execute: Callable[..., Any]
