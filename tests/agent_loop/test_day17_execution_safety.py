
from app.agent_loop.loop import RivaAgentLoop
from app.agent_loop.models import AgentDecision, DecisionType
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def make_loop(tmp_path, decision_maker):
    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(tmp_path / "day17.db"))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day17_tool_failure_does_not_crash_agent_loop(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "invalid arithmetic",
                },
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day17-safe-failure"),
        "calculate invalid",
    )

    assert len(result.executions) == 10
    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None
    assert result.response is not None


def test_day17_missing_tool_is_rejected_safely(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name=None,
                tool_arguments={},
            )

    try:
        make_loop(tmp_path, DecisionMaker()).run(
            RivaSession(session_id="day17-missing-tool"),
            "run unavailable tool",
        )
    except ValueError as exc:
        assert "tool" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected ValueError for missing tool"
        )


def test_day17_successful_tool_still_completes_normally(tmp_path):
    class DecisionMaker:
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
                        "expression": "50 / 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Safe result: 25",
            )

    dm = DecisionMaker()

    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day17-success"),
        "calculate 50 / 2",
    )

    assert dm.calls == 2
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"
    assert result.executions[0].result == "25.0"
    assert result.response == "Safe result: 25"


def test_day17_recovery_after_failure_preserves_history(tmp_path):
    class DecisionMaker:
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
                        "expression": "bad expression",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "40 + 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovered safely: 42",
            )

    dm = DecisionMaker()

    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day17-recovery"),
        "calculate 42",
    )

    assert dm.calls == 3
    assert len(result.executions) == 2

    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None

    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "42"

    assert result.response == "Recovered safely: 42"


def test_day17_multi_step_loop_has_bounded_execution(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls <= 10:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": f"{self.calls} + 1",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Bounded.",
            )

    dm = DecisionMaker()

    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day17-bounded"),
        "bounded execution",
    )

    assert len(result.executions) <= 10
    assert dm.calls <= 10




