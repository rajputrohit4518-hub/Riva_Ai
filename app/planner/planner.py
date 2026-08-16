from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)


class RivaPlanner:
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
            expression = text[10:].strip()

            return ExecutionPlan(
                goal=text,
                steps=[
                    PlanStep(
                        step_id="step_1",
                        step_type=PlanStepType.TOOL,
                        description="Calculate expression",
                        tool_name="calculator",
                        arguments={
                            "expression": expression,
                        },
                    ),
                    PlanStep(
                        step_id="step_2",
                        step_type=PlanStepType.VERIFY,
                        description="Verify calculation result",
                    ),
                ],
            )

        return ExecutionPlan(
            goal=text,
            steps=[
                PlanStep(
                    step_id="step_1",
                    step_type=PlanStepType.RESPOND,
                    description="Respond to the user",
                )
            ],
        )
