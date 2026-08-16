from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DeviceSession:
    session_id: str
    device_id: str
    connected_at: datetime
    last_seen: datetime
    active: bool = True


@dataclass(frozen=True)
class SessionResult:
    success: bool
    session_id: str
    device_id: str
    message: str
