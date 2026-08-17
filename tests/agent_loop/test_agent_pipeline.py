from app.tools.defaults import create_default_registry
from app.core.executor import ExecutionEngine
from app.planner.planner import RivaPlanner
from app.planner.executor import PlanExecutor
from app.verification.correction import SelfCorrector


def test_agent_pipeline_calculation():
    registry = create_default_registry()

    engine = ExecutionEngine(registry)
    planner = RivaPlanner()
    executor = PlanExecutor(engine)
    corrector = SelfCorrector(executor)

    plan = planner.create_plan(
        "Calculate 25 * 6"
    )

    result = corrector.run(plan)

    assert result.success is True
    assert result.attempts == 1
    assert "150" in result.outputs
    assert "Verified: 150" in result.outputs


def test_agent_pipeline_empty_input_rejected():
    planner = RivaPlanner()

    try:
        planner.create_plan("   ")
    except ValueError as exc:
        assert str(exc) == "Planning input cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError"
        )
