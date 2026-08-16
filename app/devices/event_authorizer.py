from app.devices.authorization import (
    EventAuthorization,
    EventAuthorizationResult,
)
from app.devices.events import DeviceEvent
from app.devices.sessions import DeviceSessionManager
from app.devices.trust import DeviceTrustManager


class DeviceEventAuthorizer:
    def __init__(
        self,
        trust_manager: DeviceTrustManager,
        session_manager: DeviceSessionManager,
    ) -> None:
        self._trust = trust_manager
        self._sessions = session_manager

        self._allowed_events: dict[
            str,
            set[str],
        ] = {}

    def allow(
        self,
        device_id: str,
        event_type: str,
    ) -> None:

        if not device_id.strip():
            raise ValueError(
                "Device ID cannot be empty."
            )

        if not event_type.strip():
            raise ValueError(
                "Event type cannot be empty."
            )

        self._allowed_events.setdefault(
            device_id,
            set(),
        ).add(event_type)

    def revoke(
        self,
        device_id: str,
        event_type: str,
    ) -> None:

        events = self._allowed_events.get(
            device_id,
            set(),
        )

        events.discard(event_type)

    def authorize(
        self,
        event: DeviceEvent,
    ) -> EventAuthorizationResult:

        device_id = event.source_device_id

        if not self._trust.is_trusted(
            device_id
        ):
            return EventAuthorizationResult(
                decision=EventAuthorization.DENY,
                event_type=event.event_type,
                device_id=device_id,
                reason="Source device is not trusted.",
            )

        if not self._sessions.is_connected(
            device_id
        ):
            return EventAuthorizationResult(
                decision=EventAuthorization.DENY,
                event_type=event.event_type,
                device_id=device_id,
                reason="Source device has no active session.",
            )

        allowed = self._allowed_events.get(
            device_id,
            set(),
        )

        if event.event_type not in allowed:
            return EventAuthorizationResult(
                decision=EventAuthorization.DENY,
                event_type=event.event_type,
                device_id=device_id,
                reason="Event type is not authorized.",
            )

        return EventAuthorizationResult(
            decision=EventAuthorization.ALLOW,
            event_type=event.event_type,
            device_id=device_id,
            reason="Event authorized.",
        )
