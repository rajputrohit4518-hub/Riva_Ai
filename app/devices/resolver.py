from app.devices.models import Device, DeviceType
from app.devices.registry import DeviceRegistry


class DeviceResolver:
    def __init__(
        self,
        registry: DeviceRegistry,
    ) -> None:
        self._registry = registry

    def resolve(
        self,
        device_type: DeviceType,
    ) -> Device | None:

        for device in self._registry.online():
            if device.device_type == device_type:
                return device

        return None

    def resolve_by_id(
        self,
        device_id: str,
    ) -> Device:

        device = self._registry.get(device_id)

        if not device.online:
            raise RuntimeError(
                f"Device is offline: {device_id}"
            )

        return device
