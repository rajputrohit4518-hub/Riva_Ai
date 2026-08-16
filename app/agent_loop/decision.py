from app.agent_loop.models import AgentDecision, DecisionType


class DecisionMaker:
    def decide(self, user_input: str) -> AgentDecision:
        text = user_input.strip().lower()

        if not text:
            raise ValueError("User input cannot be empty.")

        if text.startswith("calculate "):
            expression = user_input.strip()[10:].strip()

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": expression,
                },
            )

        if any(
            greeting in text
            for greeting in (
                "hello",
                "hi",
                "hey",
            )
        ):
            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Hello! I'm Riva. How can I help?",
            )

        return AgentDecision(
            decision_type=DecisionType.RESPOND,
            response=(
                "I understand your request, "
                "but I don't have a capability for it yet."
            ),
        )
