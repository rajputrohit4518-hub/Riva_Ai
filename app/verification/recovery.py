from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)


class RecoveryStrategy:
    """Creates a safer retry plan from a failed execution."""

    def recover(
        self,
        plan: ExecutionPlan,
        error: str | None,
    ) -> ExecutionPlan | None:

        if not error:
            return None

        steps = list(plan.steps)

        for index, step in enumerate(steps):
            if step.step_type != PlanStepType.TOOL:
                continue

            if step.tool_name != "calculator":
                continue

            expression = step.arguments.get("expression")

            if expression is None:
                continue

            normalized_expression = str(expression).strip()

            if not normalized_expression:
                continue

            steps[index] = PlanStep(
                step_id=step.step_id,
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": normalized_expression,
                },
                description=step.description,
            )

            return ExecutionPlan(
                goal=plan.goal,
                steps=tuple(steps),
            )

        return None
