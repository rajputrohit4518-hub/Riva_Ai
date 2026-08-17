import re

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
            entity_decision = self._entity_reference_decision(
                text,
                context,
            )

            if entity_decision is not None:
                return entity_decision

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
            re.search(
                rf"\b{re.escape(greeting)}\b",
                text,
            )
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

    def _entity_reference_decision(
        self,
        text: str,
        context: ContextSnapshot,
    ) -> AgentDecision | None:
        if not context.last_response:
            return None

        previous_result = str(context.last_response).strip()

        general_reference = any(
            phrase in text
            for phrase in (
                "what was that",
                "what was that?",
                "what was this",
                "what was this?",
                "what did you mean",
                "what did you just say",
                "what did you say",
            )
        )

        if general_reference:
            if (
                len(context.recent_messages) >= 2
                and context.recent_messages[-2].get("role") == "user"
            ):
                previous_user_message = str(
                    context.recent_messages[-2].get(
                        "content",
                        "",
                    )
                ).strip()

                if previous_user_message:
                    return AgentDecision(
                        decision_type=DecisionType.RESPOND,
                        response=previous_user_message,
                    )

            return None

        natural_reference = any(
            re.search(
                rf"\b{re.escape(reference)}\b",
                text,
            )
            for reference in (
                "this",
                "above",
            )
        )

        if natural_reference:
            if len(context.recent_messages) >= 2:
                for message in reversed(
                    context.recent_messages[:-1]
                ):
                    if message.get("role") == "user":
                        previous_user_message = str(
                            message.get("content", "")
                        ).strip()

                        if previous_user_message:
                            return AgentDecision(
                                decision_type=DecisionType.RESPOND,
                                response=previous_user_message,
                            )

            return None

        if "it" not in text:
            return None

        if not re.fullmatch(
            r"-?\d+(?:\.\d+)?",
            previous_result,
        ):
            return None

        match = re.search(
            r"\b(?:add|plus)\s+(-?\d+(?:\.\d+)?)\s+to\s+it\b",
            text,
        )

        if match:
            amount = match.group(1)

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} + {amount}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:subtract|minus)\s+(-?\d+(?:\.\d+)?)"
            r"\s+(?:from\s+)?it\b",
            text,
        )

        if match:
            amount = match.group(1)

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} - {amount}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:multiply|times)\s+it\s+by\s+"
            r"(-?\d+(?:\.\d+)?)\b",
            text,
        )

        if match:
            amount = match.group(1)

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} * {amount}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:divide)\s+it\s+by\s+"
            r"(-?\d+(?:\.\d+)?)\b",
            text,
        )

        if match:
            amount = match.group(1)

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} / {amount}"
                    ),
                },
            )

        return None
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
