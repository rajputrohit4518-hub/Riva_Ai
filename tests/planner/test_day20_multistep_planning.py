
from app.planner.models import ExecutionPlan, PlanStep, PlanStepType

def test_day20_plan_contains_ordered_steps():
    plan = ExecutionPlan(
        goal="calculate two values",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={"expression": "10 + 5"},
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={"expression": "15 * 2"},
            ),
        ),
    )

    assert len(plan.steps) == 2
    assert plan.steps[0].step_id == "step_1"
    assert plan.steps[1].step_id == "step_2"
    assert plan.steps[0].tool_name == "calculator"
    assert plan.steps[1].tool_name == "calculator"

def test_day20_plan_preserves_step_arguments():
    plan = ExecutionPlan(
        goal="calculate",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={"expression": "25 * 6"},
            ),
        ),
    )

    assert plan.steps[0].arguments["expression"] == "25 * 6"

def test_day20_plan_supports_verification_step():
    plan = ExecutionPlan(
        goal="calculate and verify",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={"expression": "10 + 5"},
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.VERIFY,
            ),
        ),
    )

    assert plan.steps[1].step_type == PlanStepType.VERIFY
