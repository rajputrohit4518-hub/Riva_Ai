from typing import List

from app.devices.models import Device


class DeviceRegistry:
    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}

    def register(
        self,
        device: Device,
    ) -> None:

        if not device.device_id.strip():
            raise ValueError(
                "Device ID cannot be empty."
            )

        if device.device_id in self._devices:
            raise ValueError(
                f"Device already registered: "
                f"{device.device_id}"
            )

        self._devices[device.device_id] = device

    def get(
        self,
        device_id: str,
    ) -> Device:

        try:
            return self._devices[device_id]
        except KeyError as exc:
            raise KeyError(
                f"Device not found: {device_id}"
            ) from exc

    def remove(
        self,
        device_id: str,
    ) -> None:

        if device_id not in self._devices:
            raise KeyError(
                f"Device not found: {device_id}"
            )

        del self._devices[device_id]

    def list(self) -> List[Device]:
        return list(self._devices.values())

    def online(self) -> List[Device]:
        return [
            device
            for device in self._devices.values()
            if device.online
        ]
