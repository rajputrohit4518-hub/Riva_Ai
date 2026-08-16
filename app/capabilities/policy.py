from app.capabilities.models import Capability, PermissionLevel


class CapabilityPolicy:
    def can_execute(
        self,
        capability: Capability,
        confirmed: bool = False,
    ) -> bool:

        if capability.permission == PermissionLevel.NONE:
            return True

        if capability.permission == PermissionLevel.CONFIRM:
            return confirmed

        if capability.permission == PermissionLevel.ELEVATED:
            return False

        return False
