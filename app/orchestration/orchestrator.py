from app.context.engine import ContextEngine
from app.core.executor import ExecutionEngine
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.orchestration.models import OrchestrationResult
from app.tools.registry import ToolRegistry


class RivaOrchestrator:
    def __init__(
        self,
        registry: ToolRegistry,
        memory_manager: MemoryManager | None = None,
        context_engine: ContextEngine | None = None,
    ) -> None:
        self._registry = registry

        self._memory = (
            memory_manager
            or MemoryManager()
        )

        self._context = (
            context_engine
            or ContextEngine(self._memory)
        )

        self._executor = ExecutionEngine(
            self._registry
        )

    def prepare(
        self,
        session: RivaSession,
        user_input: str,
    ) -> OrchestrationResult:

        user_input = user_input.strip()

        if not user_input:
            raise ValueError(
                "User input cannot be empty."
            )

        session.add_message(
            "user",
            user_input,
        )

        context = self._context.build(
            session=session,
            query=user_input,
        )

        return OrchestrationResult(
            session_id=session.session_id,
            user_input=user_input,
            context=context,
        )

    def execute_tool(
        self,
        orchestration: OrchestrationResult,
        tool_name: str,
        **kwargs,
    ) -> OrchestrationResult:

        execution = self._executor.execute(
            tool_name,
            **kwargs,
        )

        orchestration.executions.append(
            execution
        )

        return orchestration

    def respond(
        self,
        orchestration: OrchestrationResult,
        response: str,
    ) -> OrchestrationResult:

        response = response.strip()

        orchestration.response = response

        return orchestration
