from app.planner import Planner
from app.planner.models import (
    PlanStep,
    PlanStepType,
)


def test_planner_creates_multiple_steps():
    planner = Planner()

    plan = planner.plan_steps(
        goal="calculate and verify",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": "25 * 6",
                },
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.VERIFY,
            ),
        ),
    )

    assert plan.goal == "calculate and verify"
    assert len(plan.steps) == 2
    assert plan.steps[0].step_id == "step_1"
    assert plan.steps[1].step_id == "step_2"


def test_planner_preserves_step_order():
    planner = Planner()

    plan = planner.plan_steps(
        goal="multi step",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.RESPOND,
                description="first",
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.RESPOND,
                description="second",
            ),
            PlanStep(
                step_id="step_3",
                step_type=PlanStepType.RESPOND,
                description="third",
            ),
        ),
    )

    assert [
        step.step_id
        for step in plan.steps
    ] == [
        "step_1",
        "step_2",
        "step_3",
    ]


def test_planner_rejects_empty_steps():
    planner = Planner()

    try:
        planner.plan_steps(
            goal="empty",
            steps=(),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Planning steps cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_planner_rejects_empty_multi_step_goal():
    planner = Planner()

    try:
        planner.plan_steps(
            goal="   ",
            steps=(
                PlanStep(
                    step_id="step_1",
                    step_type=PlanStepType.RESPOND,
                    description="test",
                ),
            ),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Planning goal cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )
