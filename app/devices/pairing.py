import secrets
import uuid
from datetime import datetime, timedelta, timezone

from app.devices.identity import DeviceIdentity
from app.devices.pairing_models import (
    PairingRequest,
    PairingResult,
)
from app.devices.trust import DeviceTrustManager


class DevicePairingManager:
    def __init__(
        self,
        trust_manager: DeviceTrustManager,
        ttl_seconds: int = 300,
    ) -> None:

        if ttl_seconds <= 0:
            raise ValueError(
                "ttl_seconds must be greater than zero."
            )

        self._trust = trust_manager
        self._ttl = ttl_seconds
        self._requests: dict[
            str,
            PairingRequest,
        ] = {}

    def create_request(
        self,
        device_id: str,
        owner_id: str,
        fingerprint: str,
    ) -> PairingRequest:

        if not device_id.strip():
            raise ValueError(
                "Device ID cannot be empty."
            )

        if not owner_id.strip():
            raise ValueError(
                "Owner ID cannot be empty."
            )

        if not fingerprint.strip():
            raise ValueError(
                "Device fingerprint cannot be empty."
            )

        now = datetime.now(timezone.utc)

        request = PairingRequest(
            request_id=str(uuid.uuid4()),
            device_id=device_id,
            owner_id=owner_id,
            fingerprint=fingerprint,
            code=f"{secrets.randbelow(1_000_000):06d}",
            created_at=now,
            expires_at=now + timedelta(
                seconds=self._ttl
            ),
        )

        self._requests[
            request.request_id
        ] = request

        return request

    def confirm(
        self,
        request_id: str,
        code: str,
    ) -> PairingResult:

        request = self._requests.get(
            request_id
        )

        if request is None:
            return PairingResult(
                success=False,
                device_id="",
                message="Pairing request not found.",
            )

        if request.completed:
            return PairingResult(
                success=False,
                device_id=request.device_id,
                message="Pairing request already completed.",
            )

        now = datetime.now(timezone.utc)

        if now >= request.expires_at:
            return PairingResult(
                success=False,
                device_id=request.device_id,
                message="Pairing request expired.",
            )

        if not secrets.compare_digest(
            request.code,
            code,
        ):
            return PairingResult(
                success=False,
                device_id=request.device_id,
                message="Invalid pairing code.",
            )

        identity = DeviceIdentity(
            device_id=request.device_id,
            owner_id=request.owner_id,
            fingerprint=request.fingerprint,
        )

        try:
            self._trust.register_identity(
                identity
            )
        except ValueError as exc:
            return PairingResult(
                success=False,
                device_id=request.device_id,
                message=str(exc),
            )

        self._trust.trust(
            request.device_id
        )

        self._requests[
            request_id
        ] = PairingRequest(
            request_id=request.request_id,
            device_id=request.device_id,
            owner_id=request.owner_id,
            fingerprint=request.fingerprint,
            code=request.code,
            created_at=request.created_at,
            expires_at=request.expires_at,
            completed=True,
        )

        return PairingResult(
            success=True,
            device_id=request.device_id,
            message="Device paired successfully.",
        )
