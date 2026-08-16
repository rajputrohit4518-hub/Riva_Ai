from dataclasses import dataclass, field

from app.context.models import ContextSnapshot
from app.core.execution import ExecutionResult


@dataclass
class OrchestrationResult:
    session_id: str
    user_input: str
    context: ContextSnapshot
    executions: list[ExecutionResult] = field(default_factory=list)
    response: str = ""
