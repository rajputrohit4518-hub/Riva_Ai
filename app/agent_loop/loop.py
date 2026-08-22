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

        multi_step = getattr(
            self._decision,
            "supports_multi_step",
            False,
        )

        for _ in range(self.MAX_STEPS):

            if getattr(
                self._decision,
                "supports_context",
                False,
            ):
                decision = self._decision.decide(
                    user_input,
                    orchestration.context,
                )
            else:
                decision = self._decision.decide(
                    user_input
                )

            if decision.decision_type == DecisionType.MEMORY:
                if decision.memory_action == "remember":
                    self._orchestrator._memory.remember(
                        decision.memory_key or "",
                        decision.memory_value or "",
                    )

                    result = self._orchestrator.respond(
                        orchestration,
                        decision.response or "I'll remember that.",
                    )

                    if result.response:
                        session.last_response = result.response

                    return result

                if decision.memory_action == "forget":
                    self._orchestrator._memory.forget(
                        decision.memory_key or "",
                    )

                    result = self._orchestrator.respond(
                        orchestration,
                        decision.response or "I'll forget that.",
                    )

                    if result.response:
                        session.last_response = result.response

                    return result

                raise ValueError(
                    f"Unsupported memory action: {decision.memory_action}"
                )

            if decision.decision_type == DecisionType.RESPOND:
                result = self._orchestrator.respond(
                    orchestration,
                    decision.response or "",
                )

                if result.response:
                    session.last_response = result.response

                return result

            if decision.decision_type == DecisionType.USE_TOOL:

                if not decision.tool_name:
                    raise ValueError(
                        "Tool decision requires a tool name."
                    )

                self._orchestrator.execute_tool(
                    orchestration,
                    decision.tool_name,
                    **(decision.tool_arguments or {}),
                )

                latest = orchestration.executions[-1]

                if latest.status.value != "success":


                    if multi_step:


                        continue


                


                    result = self._orchestrator.respond(


                        orchestration,


                        latest.error or "Tool execution failed.",


                    )


                    return result

                tool_output = str(latest.result)

                if not multi_step:
                    result = self._orchestrator.respond(
                        orchestration,
                        tool_output,
                    )

                    if result.response:
                        session.last_response = result.response

                    return result

                continue

            raise RuntimeError(
                f"Unsupported decision: "
                f"{decision.decision_type}"
            )

        result = self._orchestrator.respond(
            orchestration,
            "I reached the maximum number of steps for this request.",
        )

        if result.response:
            session.last_response = result.response

        return result
