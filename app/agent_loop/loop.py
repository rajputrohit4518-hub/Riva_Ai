from app.agent_loop.decision import DecisionMaker
from app.agent_loop.models import DecisionType
from app.core.session import RivaSession
from app.orchestration.models import OrchestrationResult
from app.orchestration.orchestrator import RivaOrchestrator


class RivaAgentLoop:
    MAX_STEPS = 10

    def __init__(
        self,
        orchestrator: RivaOrchestrator,
        decision_maker: DecisionMaker | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._decision = decision_maker or DecisionMaker()

    def run(
        self,
        session: RivaSession,
        user_input: str,
    ) -> OrchestrationResult:

        orchestration = self._orchestrator.prepare(
            session=session,
            user_input=user_input,
        )

        # The existing/default DecisionMaker is a single-decision
        # planner. Preserve its established contract: one successful
        # tool execution produces the final response.
        multi_step = getattr(
            self._decision,
            "supports_multi_step",
            False,
        )

        for _ in range(self.MAX_STEPS):
            decision = self._decision.decide(user_input)

            if decision.decision_type == DecisionType.RESPOND:
                return self._orchestrator.respond(
                    orchestration,
                    decision.response or "",
                )

            if decision.decision_type == DecisionType.USE_TOOL:
                if not decision.tool_name:
                    raise ValueError(
                        "Tool decision requires a tool name."
                    )

                execution = self._orchestrator.execute_tool(
                    orchestration,
                    decision.tool_name,
                    **(decision.tool_arguments or {}),
                )

                latest = execution.executions[-1]

                # Failed execution always terminates the agent loop.
                if latest.status.value != "success":
                    return self._orchestrator.respond(
                        orchestration,
                        (
                            "I couldn't complete that action: "
                            f"{latest.error}"
                        ),
                    )

                # Preserve the original one-tool contract unless the
                # decision maker explicitly supports multi-step execution.
                if not multi_step:
                    return self._orchestrator.respond(
                        orchestration,
                        str(latest.result),
                    )

                # A multi-step decision maker gets another opportunity
                # to decide what to do next.
                continue

            raise RuntimeError(
                f"Unsupported decision: "
                f"{decision.decision_type}"
            )

        return self._orchestrator.respond(
            orchestration,
            "I reached the maximum number of steps for this request.",
        )

