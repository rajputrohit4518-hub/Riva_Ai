from app.agent_loop.loop import RivaAgentLoop
from app.agent_loop.models import AgentDecision, DecisionType
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def make_loop(tmp_path, decision_maker):
    database = tmp_path / "day12.db"

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


def test_day12_failed_execution_is_reported(tmp_path):
    class FailingDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "invalid arithmetic",
                },
            )

    loop = make_loop(tmp_path, FailingDecisionMaker())

    result = loop.run(
        session=RivaSession(
            session_id="day12-failure",
        ),
        user_input="calculate invalid",
    )

    assert len(result.executions) == 1
    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None
    assert "invalid arithmetic expression" in (
        result.executions[0].error.lower()
    )


def test_day12_success_after_decision_retry(tmp_path):
    class RecoveryDecisionMaker:
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
                        "expression": "invalid arithmetic",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "25 * 6",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovered successfully.",
            )

    decision_maker = RecoveryDecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day12-recovery",
        ),
        user_input="calculate 25 * 6",
    )

    assert decision_maker.calls == 3
    assert len(result.executions) == 2
    assert result.executions[0].status.value != "success"
    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "150"
    assert result.response == "Recovered successfully."


def test_day12_recovery_preserves_failed_execution(tmp_path):
    class RecoveryDecisionMaker:
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
                        "expression": "invalid arithmetic",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovery failed.",
            )

    loop = make_loop(
        tmp_path,
        RecoveryDecisionMaker(),
    )

    result = loop.run(
        session=RivaSession(
            session_id="day12-recovery-failed",
        ),
        user_input="calculate",
    )

    assert len(result.executions) == 1
    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None
    assert "invalid arithmetic expression" in (
        result.response.lower()
    ) or result.response == "Recovery failed."


def test_day12_successful_execution_needs_no_recovery(tmp_path):
    class SuccessfulDecisionMaker:
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
                        "expression": "12 + 8",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Done.",
            )

    decision_maker = SuccessfulDecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day12-success",
        ),
        user_input="calculate",
    )

    assert decision_maker.calls == 2
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"
    assert result.executions[0].result == "20"
    assert result.response == "Done."


def test_day12_missing_tool_still_rejected(tmp_path):
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

    try:
        loop.run(
            session=RivaSession(
                session_id="day12-missing-tool",
            ),
            user_input="do something",
        )
    except ValueError as exc:
        assert "tool" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected ValueError for missing tool name"
        )


def test_day12_full_multi_step_recovery_chain(tmp_path):
    class RecoveryChainDecisionMaker:
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
                        "expression": "10 + 5",
                    },
                )

            if self.calls == 3:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "15 * 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovery chain complete.",
            )

    decision_maker = RecoveryChainDecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day12-chain",
        ),
        user_input="perform recovery chain",
    )

    assert decision_maker.calls == 4
    assert len(result.executions) == 3

    assert result.executions[0].status.value != "success"
    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "15"
    assert result.executions[2].status.value == "success"
    assert result.executions[2].result == "30"

    assert result.response == "Recovery chain complete."
