from app.capabilities.models import Capability
from app.devices.models import Device, DeviceType
from app.devices.resolver import DeviceResolver


class DeviceCapabilityRouter:
    def __init__(
        self,
        resolver: DeviceResolver,
    ) -> None:
        self._resolver = resolver

    def route(
        self,
        capability: Capability,
        device_type: DeviceType,
    ) -> Device:

        device = self._resolver.resolve(
            device_type
        )

        if device is None:
            raise RuntimeError(
                f"No online device available for "
                f"capability '{capability.name}' "
                f"on device type "
                f"'{device_type.value}'."
            )

        return device

    def route_by_device(
        self,
        capability: Capability,
        device_id: str,
    ) -> Device:

        return self._resolver.resolve_by_id(
            device_id
        )
