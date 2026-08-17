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
            follow_up_response = self._conversation_response(
                text,
                context,
            )

            if follow_up_response is not None:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=follow_up_response,
                )

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

    def _conversation_response(
        self,
        text: str,
        context: ContextSnapshot,
    ) -> str | None:
        previous_message_follow_up = any(
            phrase in text
            for phrase in (
                "what did i just tell you",
                "what did i tell you",
                "what did i say",
                "what was i saying",
                "what did we just discuss",
            )
        )

        result_reference = any(
            phrase in text
            for phrase in (
                "what was the result",
                "what was the answer",
                "what was the calculation",
                "what did you calculate",
                "what did you get",
                "what was that result",
                "what was that answer",
            )
        )

        if result_reference:
            if context.last_response:
                return context.last_response

            return None

        if not previous_message_follow_up:
            return None

        if len(context.recent_messages) < 2:
            return None

        for message in reversed(context.recent_messages[:-1]):
            if message.get("role") == "user":
                content = str(
                    message.get("content", "")
                ).strip()

                if content:
                    return content

        return None
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

