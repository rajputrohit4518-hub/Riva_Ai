from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)
from app.verification.recovery import RecoveryStrategy


def test_recovery_normalizes_calculator_expression():
    strategy = RecoveryStrategy()

    plan = ExecutionPlan(
        goal="calculate 25 * 6",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": " 25 * 6 ",
                },
            ),
        ),
    )

    recovered = strategy.recover(
        plan,
        "calculator execution failed",
    )

    assert recovered is not None
    assert recovered.steps[0].arguments["expression"] == "25 * 6"


def test_recovery_preserves_plan_goal():
    strategy = RecoveryStrategy()

    plan = ExecutionPlan(
        goal="calculate 10 + 5",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": " 10 + 5 ",
                },
            ),
        ),
    )

    recovered = strategy.recover(
        plan,
        "execution failed",
    )

    assert recovered is not None
    assert recovered.goal == "calculate 10 + 5"


def test_recovery_returns_none_for_missing_error():
    strategy = RecoveryStrategy()

    plan = ExecutionPlan(
        goal="calculate 25 * 6",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": "25 * 6",
                },
            ),
        ),
    )

    assert strategy.recover(plan, None) is None


def test_recovery_returns_none_for_unsupported_tool():
    strategy = RecoveryStrategy()

    plan = ExecutionPlan(
        goal="unknown",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="unknown_tool",
            ),
        ),
    )

    assert (
        strategy.recover(
            plan,
            "tool failed",
        )
        is None
    )
