from app.agent_loop.loop import RivaAgentLoop
from app.agent_loop.models import AgentDecision, DecisionType
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def make_loop(tmp_path, decision_maker=None):
    database = tmp_path / "day10.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day10_calculator_execution(tmp_path):
    loop = make_loop(tmp_path)

    session = RivaSession(
        session_id="day10-calculator",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response == "150"
    assert len(result.executions) == 1
    assert result.executions[0].result == "150"
    assert result.executions[0].status.value == "success"


def test_day10_tool_arguments_are_forwarded(tmp_path):
    class CalculatorDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "7 * 8",
                },
            )

    loop = make_loop(
        tmp_path,
        CalculatorDecisionMaker(),
    )

    session = RivaSession(
        session_id="day10-arguments",
    )

    result = loop.run(
        session=session,
        user_input="calculate this",
    )

    assert result.response == "56"
    assert len(result.executions) == 1
    assert result.executions[0].result == "56"


def test_day10_execution_is_recorded(tmp_path):
    loop = make_loop(tmp_path)

    session = RivaSession(
        session_id="day10-recording",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 10 + 5",
    )

    assert result.executions
    assert len(result.executions) == 1

    execution = result.executions[0]

    assert execution.tool_name == "calculator"
    assert execution.result == "15"
    assert execution.status.value == "success"


def test_day10_missing_tool_is_rejected(tmp_path):
    class MissingToolDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name=None,
                tool_arguments={},
            )

    loop = make_loop(
        tmp_path,
        MissingToolDecisionMaker(),
    )

    session = RivaSession(
        session_id="day10-missing-tool",
    )

    try:
        loop.run(
            session=session,
            user_input="do something",
        )
    except ValueError as exc:
        assert "tool" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected ValueError for missing tool name"
        )


def test_day10_failed_tool_execution_is_recorded(tmp_path):
    class FailingDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "invalid arithmetic",
                },
            )

    loop = make_loop(
        tmp_path,
        FailingDecisionMaker(),
    )

    session = RivaSession(
        session_id="day10-failure",
    )

    result = loop.run(
        session=session,
        user_input="calculate invalid",
    )

    assert len(result.executions) == 1

    execution = result.executions[0]

    assert execution.status.value != "success"
    assert execution.error is not None
    assert "invalid arithmetic expression" in (
        execution.error.lower()
    )

    assert "invalid arithmetic expression" in (
        result.response.lower()
    )


def test_day10_successful_execution_preserves_result(tmp_path):
    class CalculatorDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "12 + 8",
                },
            )

    loop = make_loop(
        tmp_path,
        CalculatorDecisionMaker(),
    )

    session = RivaSession(
        session_id="day10-result",
    )

    result = loop.run(
        session=session,
        user_input="calculate",
    )

    assert result.response == "20"
    assert len(result.executions) == 1
    assert result.executions[0].result == "20"


def test_day10_multi_step_execution_preserves_all_results(
    tmp_path,
):
    class MultiStepDecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "10 + 5",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "15 * 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Multi-step complete.",
            )

    loop = make_loop(
        tmp_path,
        MultiStepDecisionMaker(),
    )

    session = RivaSession(
        session_id="day10-multi-step",
    )

    result = loop.run(
        session=session,
        user_input="do two calculations",
    )

    assert result.response == "Multi-step complete."
    assert len(result.executions) == 2

    assert result.executions[0].result == "15"
    assert result.executions[1].result == "30"

    assert all(
        execution.status.value == "success"
        for execution in result.executions
    )
