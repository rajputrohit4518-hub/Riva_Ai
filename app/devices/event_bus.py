from collections import defaultdict
from collections.abc import Callable

from app.devices.events import DeviceEvent


EventHandler = Callable[[DeviceEvent], None]


class DeviceEventBus:
    def __init__(self) -> None:
        self._handlers: dict[
            str,
            list[EventHandler],
        ] = defaultdict(list)

        self._history: list[DeviceEvent] = []

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:

        if not event_type.strip():
            raise ValueError(
                "Event type cannot be empty."
            )

        if handler not in self._handlers[
            event_type
        ]:
            self._handlers[
                event_type
            ].append(handler)

    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:

        handlers = self._handlers.get(
            event_type,
            [],
        )

        if handler in handlers:
            handlers.remove(handler)

    def publish(
        self,
        event: DeviceEvent,
    ) -> None:

        self._history.append(event)

        handlers = list(
            self._handlers.get(
                event.event_type,
                [],
            )
        )

        for handler in handlers:
            handler(event)

    def history(self) -> list[DeviceEvent]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()
