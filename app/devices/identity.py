from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceIdentity:
    device_id: str
    owner_id: str
    fingerprint: str


@dataclass(frozen=True)
class TrustRecord:
    device_id: str
    trusted: bool = False
