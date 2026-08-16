from dataclasses import dataclass
from enum import Enum


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    PHONE = "phone"
    TABLET = "tablet"
    WATCH = "watch"
    CAR = "car"
    HOME = "home"


@dataclass(frozen=True)
class Device:
    device_id: str
    name: str
    device_type: DeviceType
    online: bool = True
