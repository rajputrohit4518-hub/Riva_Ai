from app.brain.command_compiler import RivaCommandCompiler
from app.brain.intent_parser import RivaIntentParser
from app.brain.intent_models import IntentType
from app.command_router import UnifiedCommandRouter


class RivaCommandPipeline:
    def __init__(
        self,
        parser: RivaIntentParser,
        compiler: RivaCommandCompiler,
        router: UnifiedCommandRouter,
    ) -> None:
        self._parser = parser
        self._compiler = compiler
        self._router = router

    def process(self, text: str):
        intent = self._parser.parse(text)

        if intent.intent_type != IntentType.COMMAND:
            return {
                "success": False,
                "stage": "intent",
                "intent_type": intent.intent_type.value,
                "message": "Input is not an executable command.",
                "intent": intent,
            }

        try:
            request = self._compiler.compile(intent)
        except ValueError as exc:
            return {
                "success": False,
                "stage": "compile",
                "intent_type": intent.intent_type.value,
                "message": str(exc),
                "intent": intent,
            }

        result = self._router.execute(request)

        return {
            "success": result.success,
            "stage": "execute",
            "intent_type": intent.intent_type.value,
            "message": result.message,
            "command_id": result.command_id,
            "device_id": result.device_id,
            "result": result,
        }
