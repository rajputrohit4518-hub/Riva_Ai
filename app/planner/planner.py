from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)


class Planner:
    """Creates deterministic execution plans."""

    def plan(
        self,
        goal: str,
        tool_name: str,
        arguments: dict | None = None,
    ) -> ExecutionPlan:
        normalized_goal = goal.strip()

        if not normalized_goal:
            raise ValueError(
                "Planning goal cannot be empty."
            )

        if not tool_name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        return ExecutionPlan(
            goal=normalized_goal,
            steps=(
                PlanStep(
                    tool_name=tool_name.strip(),
                    arguments=dict(arguments or {}),
                    step_id="step_1",
                    step_type=PlanStepType.TOOL,
                ),
            ),
        )

    def plan_steps(
        self,
        goal: str,
        steps: list[PlanStep] | tuple[PlanStep, ...],
    ) -> ExecutionPlan:
        normalized_goal = goal.strip()

        if not normalized_goal:
            raise ValueError(
                "Planning goal cannot be empty."
            )

        normalized_steps = tuple(steps)

        if not normalized_steps:
            raise ValueError(
                "Planning steps cannot be empty."
            )

        return ExecutionPlan(
            goal=normalized_goal,
            steps=normalized_steps,
        )


class RivaPlanner(Planner):
    """Public Riva planner interface."""

    def create_plan(
        self,
        user_input: str,
    ) -> ExecutionPlan:
        text = user_input.strip()

        if not text:
            raise ValueError(
                "Planning input cannot be empty."
            )

        lowered = text.lower()

        if lowered.startswith("calculate "):
            expression = text[len("calculate "):].strip()

            return ExecutionPlan(
                goal=text,
                steps=(
                    PlanStep(
                        tool_name="calculator",
                        arguments={
                            "expression": expression,
                        },
                        step_id="step_1",
                        step_type=PlanStepType.TOOL,
                    ),
                    PlanStep(
                        step_id="step_2",
                        step_type=PlanStepType.VERIFY,
                        description="Verify calculator result",
                    ),
                ),
            )

        return ExecutionPlan(
            goal=text,
            steps=(
                PlanStep(
                    step_id="step_1",
                    step_type=PlanStepType.RESPOND,
                    description=text,
                ),
            ),
        )
