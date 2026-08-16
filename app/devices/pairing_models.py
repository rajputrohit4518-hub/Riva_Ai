from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PairingRequest:
    request_id: str
    device_id: str
    owner_id: str
    fingerprint: str
    code: str
    created_at: datetime
    expires_at: datetime
    completed: bool = False


@dataclass(frozen=True)
class PairingResult:
    success: bool
    device_id: str
    message: str
