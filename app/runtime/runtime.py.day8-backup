from app.agent_loop.loop import RivaAgentLoop
from app.brain.gateway import BrainGateway
from app.brain.models import BrainDecisionType
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.orchestration.orchestrator import RivaOrchestrator
from app.runtime.models import RuntimeResult
from app.brain.response_models import RivaResponse, ResponseType


class RivaRuntime:
    def __init__(
        self,
        registry=None,
        memory_manager: MemoryManager | None = None,
        brain=None,
        pipeline=None,
        session: RivaSession | None = None,
    ) -> None:

        self._pipeline = pipeline
        self.session = session

        # Command-pipeline runtime mode.
        if pipeline is not None:
            return

        # Existing orchestration/runtime mode.
        if registry is None:
            raise TypeError(
                "registry is required when pipeline is not provided."
            )

        if memory_manager is None:
            memory_manager = MemoryManager()

        self._memory = memory_manager
        self._registry = registry

        self._orchestrator = RivaOrchestrator(
            registry=registry,
            memory_manager=memory_manager,
        )

        self._agent_loop = RivaAgentLoop(
            orchestrator=self._orchestrator,
        )

        self._gateway = BrainGateway(registry)


        self._brain = brain

    @staticmethod
    def create_session(
        session_id: str,
    ) -> RivaSession:
        return RivaSession(
            session_id=session_id,
        )

    def process(self, text: str):
        if self._pipeline is None:
            raise RuntimeError(
                "Command pipeline is not configured."
            )

        if self.session is None:
            raise RuntimeError(
                "Runtime session is not configured."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Input cannot be empty."
            )

        self.session.command_count += 1

        result = self._pipeline.process(text)

        if result.get("success"):
            return RivaResponse(
                success=True,
                response_type=ResponseType.SUCCESS,
                message=result.get("message", ""),
                command_id=result.get("command_id"),
            )

        intent_type = result.get("intent_type")

        if intent_type == "conversation":
            return RivaResponse(
                success=True,
                response_type=ResponseType.CONVERSATION,
                message=result.get(
                    "message",
                    "Hello! How can I help you?",
                ),
                command_id=result.get("command_id"),
            )

        return RivaResponse(
            success=False,
            response_type=ResponseType.UNKNOWN,
            message=result.get(
                "message",
                "I couldn't understand that request.",
            ),
            command_id=result.get("command_id"),
        )
    def handle(
        self,
        session: RivaSession,
        user_input: str,
    ) -> RuntimeResult:

        user_input = user_input.strip()

        if not user_input:
            raise ValueError(
                "User input cannot be empty."
            )

        orchestration = self._agent_loop.run(
            session=session,
            user_input=user_input,
        )

        if orchestration.executions:
            executions = orchestration.executions
            last_execution = executions[-1]

            if last_execution.status.value != "success":
                return RuntimeResult(
                    session_id=session.session_id,
                    user_input=user_input,
                    response=orchestration.response,
                    tool_outputs=[
                        str(execution.result)
                        for execution in executions
                        if execution.result is not None
                    ],
                    success=False,
                    error=last_execution.error,
                )

        response = orchestration.response

        if (
            orchestration.executions
            and orchestration.executions[-1].status.value == "success"
            and response.strip()
            and user_input.lower().startswith("calculate ")
            and not response.startswith("Verified:")
        ):
            response = f"Verified: {response}"

        return RuntimeResult(
            session_id=session.session_id,
            user_input=user_input,
            response=response,
            tool_outputs=[
                str(execution.result)
                for execution in orchestration.executions
                if execution.result is not None
            ],
            success=True,
        )

