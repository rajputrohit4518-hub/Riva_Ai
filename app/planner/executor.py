from dataclasses import dataclass, field

from app.core.executor import ExecutionEngine
from app.planner.models import ExecutionPlan, PlanStepType


@dataclass(frozen=True)
class PlanStepResult:
    step_id: str
    step_type: PlanStepType
    success: bool
    output: str | None = None
    error: str | None = None


@dataclass
class PlanExecutionResult:
    success: bool
    outputs: list[str] = field(default_factory=list)
    error: str | None = None
    step_results: list[PlanStepResult] = field(
        default_factory=list
    )


class PlanExecutor:
    def __init__(self, execution_engine: ExecutionEngine) -> None:
        self._engine = execution_engine

    def execute(
        self,
        plan: ExecutionPlan,
    ) -> PlanExecutionResult:

        outputs: list[str] = []
        step_results: list[PlanStepResult] = []
        last_result: str | None = None

        for step in plan.steps:

            if step.step_type == PlanStepType.TOOL:
                if not step.tool_name:
                    error = f"{step.step_id}: missing tool name"

                    step_results.append(
                        PlanStepResult(
                            step_id=step.step_id,
                            step_type=step.step_type,
                            success=False,
                            error=error,
                        )
                    )

                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=error,
                        step_results=step_results,
                    )

                execution = self._engine.execute(
                    step.tool_name,
                    **step.arguments,
                )

                if execution.status.value != "success":
                    error = (
                        f"{step.step_id}: "
                        f"{execution.error}"
                    )

                    step_results.append(
                        PlanStepResult(
                            step_id=step.step_id,
                            step_type=step.step_type,
                            success=False,
                            error=error,
                        )
                    )

                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=error,
                        step_results=step_results,
                    )

                last_result = str(execution.result)
                outputs.append(last_result)

                step_results.append(
                    PlanStepResult(
                        step_id=step.step_id,
                        step_type=step.step_type,
                        success=True,
                        output=last_result,
                    )
                )

            elif step.step_type == PlanStepType.VERIFY:
                if last_result is None:
                    error = (
                        f"{step.step_id}: "
                        "nothing to verify"
                    )

                    step_results.append(
                        PlanStepResult(
                            step_id=step.step_id,
                            step_type=step.step_type,
                            success=False,
                            error=error,
                        )
                    )

                    return PlanExecutionResult(
                        success=False,
                        outputs=outputs,
                        error=error,
                        step_results=step_results,
                    )

                verified = f"Verified: {last_result}"
                outputs.append(verified)

                step_results.append(
                    PlanStepResult(
                        step_id=step.step_id,
                        step_type=step.step_type,
                        success=True,
                        output=verified,
                    )
                )

            elif step.step_type == PlanStepType.RESPOND:
                outputs.append(step.description)

                step_results.append(
                    PlanStepResult(
                        step_id=step.step_id,
                        step_type=step.step_type,
                        success=True,
                        output=step.description,
                    )
                )

            else:
                error = (
                    f"{step.step_id}: "
                    "unsupported step type"
                )

                step_results.append(
                    PlanStepResult(
                        step_id=step.step_id,
                        step_type=step.step_type,
                        success=False,
                        error=error,
                    )
                )

                return PlanExecutionResult(
                    success=False,
                    outputs=outputs,
                    error=error,
                    step_results=step_results,
                )

        return PlanExecutionResult(
            success=True,
            outputs=outputs,
            step_results=step_results,
        )
