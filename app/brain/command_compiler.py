import uuid

from app.brain.intent_models import (
    IntentType,
    ParsedIntent,
)
from app.core_command_models import CommandRequest
from app.devices.models import DeviceType


class RivaCommandCompiler:
    def compile(
        self,
        intent: ParsedIntent,
    ) -> CommandRequest:

        if intent.intent_type != IntentType.COMMAND:
            raise ValueError(
                "Only command intents can be compiled."
            )

        if not intent.capability_name:
            raise ValueError(
                "Command intent requires a capability."
            )

        device_type = DeviceType.DESKTOP

        if intent.device_type:
            try:
                device_type = DeviceType(
                    intent.device_type
                )
            except ValueError as exc:
                raise ValueError(
                    f"Unknown device type: "
                    f"{intent.device_type}"
                ) from exc

        return CommandRequest(
            command_id=str(uuid.uuid4()),
            capability_name=intent.capability_name,
            device_type=device_type,
            arguments=dict(intent.arguments),
        )
