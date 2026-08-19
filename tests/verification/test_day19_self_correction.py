from app.core.executor import ExecutionEngine
from app.planner.executor import PlanExecutor
from app.planner.models import ExecutionPlan, PlanStep, PlanStepType
from app.tools.defaults import create_default_registry
from app.verification.correction import SelfCorrector


def create_executor():
    return PlanExecutor(
        ExecutionEngine(create_default_registry())
    )


def test_day19_correct_method_is_called():
    class CorrectingSelfCorrector(SelfCorrector):
        def __init__(self, executor):
            super().__init__(executor=executor, max_attempts=2)
            self.calls = 0

        def correct(self, plan, error):
            self.calls += 1
            return plan

    corrector = CorrectingSelfCorrector(create_executor())

    plan = ExecutionPlan(
        goal="invalid",
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
    assert corrector.calls == 2


def test_day19_success_never_calls_correct():
    class CorrectingSelfCorrector(SelfCorrector):
        def __init__(self, executor):
            super().__init__(executor=executor)
            self.calls = 0

        def correct(self, plan, error):
            self.calls += 1
            return plan

    corrector = CorrectingSelfCorrector(create_executor())

    plan = ExecutionPlan(
        goal="25 * 6",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="calculator",
                arguments={"expression": "25 * 6"},
            ),
        ),
    )

    result = corrector.run(plan)

    assert result.success is True
    assert result.outputs == ["150"]
    assert corrector.calls == 0


def test_day19_corrected_plan_can_recover():
    class CorrectingSelfCorrector(SelfCorrector):
        def __init__(self, executor):
            super().__init__(executor=executor, max_attempts=2)
            self.calls = 0

        def correct(self, plan, error):
            self.calls += 1
            return ExecutionPlan(
                goal="fixed",
                steps=(
                    PlanStep(
                        step_id="step_1",
                        step_type=PlanStepType.TOOL,
                        tool_name="calculator",
                        arguments={"expression": "20 + 22"},
                    ),
                ),
            )

    corrector = CorrectingSelfCorrector(create_executor())

    bad_plan = ExecutionPlan(
        goal="bad",
        steps=(
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                tool_name="missing_tool",
                arguments={},
            ),
        ),
    )

    result = corrector.run(bad_plan)

    assert result.success is True
    assert result.attempts == 2
    assert result.outputs == ["42"]
    assert corrector.calls == 1
