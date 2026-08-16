from app.capabilities.registry import CapabilityRegistry
from app.devices.models import DeviceType
from app.devices.router import DeviceCapabilityRouter
from app.core_command_models import (
    CommandRequest,
    CommandResult,
)


class UnifiedCommandRouter:
    def __init__(
        self,
        capabilities: CapabilityRegistry,
        devices: DeviceCapabilityRouter,
    ) -> None:
        self._capabilities = capabilities
        self._devices = devices

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        try:
            capability = self._capabilities.get(
                request.capability_name
            )
        except KeyError:
            return CommandResult(
                success=False,
                command_id=request.command_id,
                capability_name=request.capability_name,
                device_id=None,
                message=(
                    f"Capability not found: "
                    f"{request.capability_name}"
                ),
            )

        try:
            device = self._devices.route(
                capability,
                request.device_type,
            )
        except RuntimeError as exc:
            return CommandResult(
                success=False,
                command_id=request.command_id,
                capability_name=request.capability_name,
                device_id=None,
                message=str(exc),
            )

        try:
            result = capability.execute(
                **request.arguments
            )
        except Exception as exc:
            return CommandResult(
                success=False,
                command_id=request.command_id,
                capability_name=request.capability_name,
                device_id=device.device_id,
                message=f"Capability execution failed: {exc}",
            )

        success = getattr(
            result,
            "success",
            True,
        )

        message = getattr(
            result,
            "message",
            str(result),
        )

        return CommandResult(
            success=success,
            command_id=request.command_id,
            capability_name=request.capability_name,
            device_id=device.device_id,
            message=message,
            data=result,
        )
