from app.brain.intent_models import IntentType
from app.brain.response_models import (
    ResponseType,
    RivaResponse,
)


class RivaResponseBuilder:

    def from_pipeline_result(
        self,
        result: dict,
    ) -> RivaResponse:

        intent_type = result.get(
            "intent_type"
        )

        if intent_type == IntentType.CONVERSATION.value:
            return RivaResponse(
                response_type=ResponseType.CONVERSATION,
                message="Hello! I'm Riva. How can I help?",
                success=True,
            )

        if intent_type == IntentType.UNKNOWN.value:
            return RivaResponse(
                response_type=ResponseType.UNKNOWN,
                message=(
                    "I'm not sure what you want me "
                    "me to do yet."
                ),
                success=False,
            )

        if result.get("success") is True:
            return RivaResponse(
                response_type=ResponseType.SUCCESS,
                message=result.get(
                    "message",
                    "Done.",
                ),
                success=True,
                data=result.get("result"),
                command_id=result.get(
                    "command_id"
                ),
            )

        return RivaResponse(
            response_type=ResponseType.FAILURE,
            message=result.get(
                "message",
                "I couldn't complete that request.",
            ),
            success=False,
            command_id=result.get(
                "command_id"
            ),
        )
