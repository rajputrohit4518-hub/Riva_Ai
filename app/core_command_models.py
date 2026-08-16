from dataclasses import dataclass
from typing import Any

from app.devices.models import DeviceType


@dataclass(frozen=True)
class CommandRequest:
    command_id: str
    capability_name: str
    device_type: DeviceType
    arguments: dict[str, Any]


@dataclass(frozen=True)
class CommandResult:
    success: bool
    command_id: str
    capability_name: str
    device_id: str | None
    message: str
    data: Any = None
