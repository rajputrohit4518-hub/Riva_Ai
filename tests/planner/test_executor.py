from app.tools.defaults import create_default_registry
from app.core.executor import ExecutionEngine
from app.planner.executor import PlanExecutor
from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)


def test_plan_executor_records_tool_execution():
    engine = ExecutionEngine(
        create_default_registry()
    )

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

    result = PlanExecutor(engine).execute(plan)

    assert result.success is True
    assert result.outputs == ["150"]

    assert len(result.step_results) == 1

    step_result = result.step_results[0]

    assert step_result.step_id == "step_1"
    assert step_result.step_type == PlanStepType.TOOL
    assert step_result.success is True
    assert step_result.output == "150"
    assert step_result.error is None


def test_plan_executor_records_verification():
    engine = ExecutionEngine(
        create_default_registry()
    )

    plan = ExecutionPlan(
        goal="calculate and verify 25 * 6",
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
                description="",
            ),
        ),
    )

    result = PlanExecutor(engine).execute(plan)

    assert result.success is True
    assert result.outputs == [
        "150",
        "Verified: 150",
    ]

    assert len(result.step_results) == 2

    verification = result.step_results[1]

    assert verification.step_id == "step_2"
    assert verification.step_type == PlanStepType.VERIFY
    assert verification.success is True
    assert verification.output == "Verified: 150"
    assert verification.error is None
