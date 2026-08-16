from app.capabilities.models import Capability


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(
        self,
        capability: Capability,
    ) -> None:

        name = capability.name.strip()

        if not name:
            raise ValueError(
                "Capability name cannot be empty."
            )

        if name in self._capabilities:
            raise ValueError(
                f"Capability already registered: {name}"
            )

        self._capabilities[name] = capability

    def get(
        self,
        name: str,
    ) -> Capability:

        try:
            return self._capabilities[name]
        except KeyError as exc:
            raise KeyError(
                f"Capability not found: {name}"
            ) from exc

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._capabilities

    def names(self) -> list[str]:
        return sorted(self._capabilities)
