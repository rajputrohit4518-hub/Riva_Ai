from app.core.executor import ExecutionEngine
from app.planner.executor import PlanExecutor
from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)
from app.tools.defaults import create_default_registry


def test_executor_runs_multiple_steps_in_order():
    engine = ExecutionEngine(
        create_default_registry()
    )

    plan = ExecutionPlan(
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

    result = PlanExecutor(engine).execute(plan)

    assert result.success is True

    assert result.outputs == [
        "150",
        "Verified: 150",
    ]

    assert [
        item.step_id
        for item in result.step_results
    ] == [
        "step_1",
        "step_2",
    ]


def test_executor_stops_after_failed_step():
    engine = ExecutionEngine(
        create_default_registry()
    )

    plan = ExecutionPlan(
        goal="bad multi step",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="missing_tool",
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.RESPOND,
                description="should not execute",
            ),
        ),
    )

    result = PlanExecutor(engine).execute(plan)

    assert result.success is False
    assert result.outputs == []

    assert len(result.step_results) == 1
    assert result.step_results[0].step_id == "step_1"
    assert result.step_results[0].success is False
