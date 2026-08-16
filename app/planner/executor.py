from dataclasses import dataclass, field

from app.core.executor import ExecutionEngine
from app.planner.models import ExecutionPlan, PlanStepType


@dataclass
class PlanExecutionResult:
    success: bool
    outputs: list[str] = field(default_factory=list)
    error: str | None = None


class PlanExecutor:
    def __init__(self, execution_engine: ExecutionEngine) -> None:
        self._engine = execution_engine

    def execute(
        self,
        plan: ExecutionPlan,
    ) -> PlanExecutionResult:

        outputs: list[str] = []
        last_result: str | None = None

        for step in plan.steps:

            if step.step_type == PlanStepType.TOOL:
                if not step.tool_name:
                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=f"{step.step_id}: missing tool name",
                    )

                execution = self._engine.execute(
                    step.tool_name,
                    **step.arguments,
                )

                if execution.status.value != "success":
                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=(
                            f"{step.step_id}: "
                            f"{execution.error}"
                        ),
                    )

                last_result = str(execution.result)
                outputs.append(last_result)

            elif step.step_type == PlanStepType.VERIFY:
                if last_result is None:
                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=(
                            f"{step.step_id}: "
                            "nothing to verify"
                        ),
                    )

                outputs.append(
                    f"Verified: {last_result}"
                )

            elif step.step_type == PlanStepType.RESPOND:
                outputs.append(step.description)

            else:
                return PlanExecutionResult(
                    success=False,
                    outputs=outputs,
                    error=(
                        f"{step.step_id}: "
                        "unsupported step type"
                    ),
                )

        return PlanExecutionResult(
            success=True,
            outputs=outputs,
        )
