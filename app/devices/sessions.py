import uuid
from datetime import datetime, timezone

from app.devices.session_models import (
    DeviceSession,
    SessionResult,
)
from app.devices.trust import DeviceTrustManager


class DeviceSessionManager:
    def __init__(
        self,
        trust_manager: DeviceTrustManager,
    ) -> None:
        self._trust = trust_manager
        self._sessions: dict[
            str,
            DeviceSession,
        ] = {}

    def connect(
        self,
        device_id: str,
    ) -> SessionResult:

        if not self._trust.is_trusted(
            device_id
        ):
            return SessionResult(
                success=False,
                session_id="",
                device_id=device_id,
                message=(
                    "Device is not trusted."
                ),
            )

        now = datetime.now(timezone.utc)

        session = DeviceSession(
            session_id=str(uuid.uuid4()),
            device_id=device_id,
            connected_at=now,
            last_seen=now,
            active=True,
        )

        self._sessions[
            session.session_id
        ] = session

        return SessionResult(
            success=True,
            session_id=session.session_id,
            device_id=device_id,
            message="Device session connected.",
        )

    def get(
        self,
        session_id: str,
    ) -> DeviceSession:

        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(
                f"Session not found: {session_id}"
            ) from exc

    def heartbeat(
        self,
        session_id: str,
    ) -> SessionResult:

        session = self.get(session_id)

        if not session.active:
            return SessionResult(
                success=False,
                session_id=session_id,
                device_id=session.device_id,
                message="Session is inactive.",
            )

        now = datetime.now(timezone.utc)

        self._sessions[
            session_id
        ] = DeviceSession(
            session_id=session.session_id,
            device_id=session.device_id,
            connected_at=session.connected_at,
            last_seen=now,
            active=True,
        )

        return SessionResult(
            success=True,
            session_id=session_id,
            device_id=session.device_id,
            message="Heartbeat accepted.",
        )

    def disconnect(
        self,
        session_id: str,
    ) -> SessionResult:

        session = self.get(session_id)

        self._sessions[
            session_id
        ] = DeviceSession(
            session_id=session.session_id,
            device_id=session.device_id,
            connected_at=session.connected_at,
            last_seen=session.last_seen,
            active=False,
        )

        return SessionResult(
            success=True,
            session_id=session_id,
            device_id=session.device_id,
            message="Device session disconnected.",
        )

    def active_sessions(
        self,
    ) -> list[DeviceSession]:

        return [
            session
            for session in self._sessions.values()
            if session.active
        ]

    def is_connected(
        self,
        device_id: str,
    ) -> bool:

        return any(
            session.device_id == device_id
            and session.active
            for session in self._sessions.values()
        )
