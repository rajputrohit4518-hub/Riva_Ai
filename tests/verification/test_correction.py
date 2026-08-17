from app.core.executor import ExecutionEngine
from app.planner.executor import PlanExecutor
from app.planner.models import (
    ExecutionPlan,
    PlanStep,
    PlanStepType,
)
from app.tools.defaults import create_default_registry
from app.verification.correction import SelfCorrector
from app.verification.models import VerificationStatus, VerificationResult


def create_executor():
    return PlanExecutor(
        ExecutionEngine(
            create_default_registry()
        )
    )


def test_self_corrector_succeeds_for_valid_plan():
    corrector = SelfCorrector(
        executor=create_executor(),
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

    result = corrector.run(plan)

    assert result.success is True
    assert result.attempts == 1
    assert result.outputs == ["150"]


def test_self_corrector_rejects_invalid_plan():
    corrector = SelfCorrector(
        executor=create_executor(),
        max_attempts=2,
    )

    plan = ExecutionPlan(
        goal="invalid tool",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="missing_tool",
                arguments={},
            ),
        ),
    )

    result = corrector.run(plan)

    assert result.success is False
    assert result.attempts == 2
    assert result.error is not None
    assert len(result.outputs) == 0


def test_self_corrector_validates_final_output():
    corrector = SelfCorrector(
        executor=create_executor(),
    )

    plan = ExecutionPlan(
        goal="calculate 10 + 5",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={
                    "expression": "10 + 5",
                },
            ),
            PlanStep(
                step_id="step_2",
                step_type=PlanStepType.VERIFY,
            ),
        ),
    )

    result = corrector.run(plan)

    assert result.success is True
    assert result.attempts == 1
    assert result.outputs == [
        "15",
        "Verified: 15",
    ]


def test_self_corrector_rejects_zero_attempts():
    try:
        SelfCorrector(
            executor=create_executor(),
            max_attempts=0,
        )
    except ValueError as exc:
        assert str(exc) == "max_attempts must be at least 1."
    else:
        raise AssertionError(
            "Expected ValueError"
        )
