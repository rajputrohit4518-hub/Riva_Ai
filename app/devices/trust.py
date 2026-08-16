from app.devices.identity import DeviceIdentity, TrustRecord


class DeviceTrustManager:
    def __init__(self) -> None:
        self._identities: dict[str, DeviceIdentity] = {}
        self._trust: dict[str, TrustRecord] = {}

    def register_identity(
        self,
        identity: DeviceIdentity,
    ) -> None:

        if not identity.device_id.strip():
            raise ValueError(
                "Device ID cannot be empty."
            )

        if not identity.owner_id.strip():
            raise ValueError(
                "Owner ID cannot be empty."
            )

        if not identity.fingerprint.strip():
            raise ValueError(
                "Device fingerprint cannot be empty."
            )

        if identity.device_id in self._identities:
            raise ValueError(
                f"Device identity already registered: "
                f"{identity.device_id}"
            )

        self._identities[
            identity.device_id
        ] = identity

        self._trust[
            identity.device_id
        ] = TrustRecord(
            device_id=identity.device_id,
            trusted=False,
        )

    def get_identity(
        self,
        device_id: str,
    ) -> DeviceIdentity:

        try:
            return self._identities[device_id]
        except KeyError as exc:
            raise KeyError(
                f"Device identity not found: {device_id}"
            ) from exc

    def trust(
        self,
        device_id: str,
    ) -> None:

        if device_id not in self._identities:
            raise KeyError(
                f"Device identity not found: {device_id}"
            )

        self._trust[
            device_id
        ] = TrustRecord(
            device_id=device_id,
            trusted=True,
        )

    def revoke(
        self,
        device_id: str,
    ) -> None:

        if device_id not in self._identities:
            raise KeyError(
                f"Device identity not found: {device_id}"
            )

        self._trust[
            device_id
        ] = TrustRecord(
            device_id=device_id,
            trusted=False,
        )

    def is_trusted(
        self,
        device_id: str,
    ) -> bool:

        record = self._trust.get(device_id)

        if record is None:
            return False

        return record.trusted
