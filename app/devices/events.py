from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DeviceEvent:
    event_id: str
    event_type: str
    source_device_id: str
    target_device_id: str | None
    payload: dict[str, Any]
    created_at: datetime

    @classmethod
    def create(
        cls,
        event_type: str,
        source_device_id: str,
        payload: dict[str, Any],
        target_device_id: str | None = None,
    ) -> "DeviceEvent":

        import uuid

        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source_device_id=source_device_id,
            target_device_id=target_device_id,
            payload=dict(payload),
            created_at=datetime.now(timezone.utc),
        )
