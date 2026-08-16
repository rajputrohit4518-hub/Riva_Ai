from dataclasses import dataclass

from app.devices.models import Device


@dataclass(frozen=True)
class RoutingDecision:
    capability_name: str
    device: Device
