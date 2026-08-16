from dataclasses import dataclass
from enum import Enum


class EventAuthorization(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class EventAuthorizationResult:
    decision: EventAuthorization
    event_type: str
    device_id: str
    reason: str
