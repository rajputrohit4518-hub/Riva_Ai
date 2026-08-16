from app.devices.event_bus import DeviceEventBus
from app.devices.events import DeviceEvent


class DeviceEventRouter:
    def __init__(
        self,
        bus: DeviceEventBus,
    ) -> None:
        self._bus = bus

    def publish(
        self,
        event: DeviceEvent,
    ) -> None:

        self._bus.publish(event)
