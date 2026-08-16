from app.agent_loop.models import AgentDecision, DecisionType
from app.context.models import ContextSnapshot


class DecisionMaker:
    supports_context = True

    def decide(
        self,
        user_input: str,
        context: ContextSnapshot | None = None,
    ) -> AgentDecision:
        text = user_input.strip().lower()

        if not text:
            raise ValueError("User input cannot be empty.")

        if context is not None:
            memory_response = self._memory_response(
                text,
                context,
            )

            if memory_response is not None:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=memory_response,
                )

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

    def _memory_response(
        self,
        text: str,
        context: ContextSnapshot,
    ) -> str | None:
        if not context.memories:
            return None

        memory_question = any(
            phrase in text
            for phrase in (
                "what is my",
                "what's my",
                "what do i",
                "what did i",
                "do you remember",
                "remember my",
            )
        )

        if not memory_question:
            return None

        for memory in context.memories:
            if memory.value:
                return memory.value

        return None
