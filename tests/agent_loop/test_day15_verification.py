
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
            MemoryStore(str(tmp_path / "day15.db"))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day15_successful_result_is_preserved(tmp_path):
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
                    tool_arguments={"expression": "25 * 6"},
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Verified result: 150",
            )

    dm = DecisionMaker()
    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day15-verified"),
        "calculate 25 * 6",
    )

    assert dm.calls == 2
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"
    assert result.executions[0].result == "150"
    assert result.response == "Verified result: 150"


def test_day15_failed_result_remains_recorded(tmp_path):
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
                    tool_arguments={"expression": "bad expression"},
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Verification detected failure.",
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day15-failed"),
        "calculate",
    )

    execution = result.executions[0]

    assert execution.status.value != "success"
    assert execution.error is not None
    assert result.response == "Verification detected failure."


def test_day15_recovery_result_replaces_failed_attempt_as_final_result(tmp_path):
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
                    tool_arguments={"expression": "invalid arithmetic"},
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={"expression": "20 + 5"},
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Verified after recovery: 25",
            )

    dm = DecisionMaker()

    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day15-recovery"),
        "calculate 20 + 5",
    )

    assert dm.calls == 3
    assert len(result.executions) == 2
    assert result.executions[0].status.value != "success"
    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "25"
    assert result.response == "Verified after recovery: 25"


def test_day15_multi_step_verified_history_is_ordered(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            expressions = {
                1: "5 + 5",
                2: "10 * 2",
                3: "20 + 1",
            }

            if self.calls <= 3:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": expressions[self.calls],
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="All results verified.",
            )

    dm = DecisionMaker()

    result = make_loop(tmp_path, dm).run(
        RivaSession(session_id="day15-history"),
        "perform verified calculations",
    )

    assert dm.calls == 4
    assert [e.result for e in result.executions] == ["10", "20", "21"]
    assert all(
        e.status.value == "success"
        for e in result.executions
    )
    assert result.response == "All results verified."
