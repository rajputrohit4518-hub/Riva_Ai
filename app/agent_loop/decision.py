import re

from app.agent_loop.models import AgentDecision, DecisionType
from app.context.models import ContextSnapshot
from app.context.resolver import ContextResolver
from app.intent.models import IntentType
from app.intent.resolver import IntentResolver


class DecisionMaker:
    supports_context = True

    def __init__(self) -> None:
        self._context_resolver = ContextResolver()
        self._intent_resolver = IntentResolver()

    def decide(
        self,
        user_input: str,
        context: ContextSnapshot | None = None,
    ) -> AgentDecision:
        text = user_input.strip().lower()

        if not text:
            raise ValueError("User input cannot be empty.")

        # Explicit memory commands must always be handled before
        # contextual memory lookup. Otherwise a command such as
        # "remember my favorite language is Rust" can be intercepted
        # by the previous stored value.
        initial_intent = self._intent_resolver.resolve(user_input)

        if initial_intent.intent_type == IntentType.MEMORY:
            if initial_intent.memory_action == "remember":
                return AgentDecision(
                    decision_type=DecisionType.MEMORY,
                    memory_action="remember",
                    memory_key=initial_intent.memory_key,
                    memory_value=initial_intent.memory_value,
                    response=(
                        f"I'll remember that "
                        f"{initial_intent.memory_key} is "
                        f"{initial_intent.memory_value}."
                    ),
                )

            if initial_intent.memory_action == "forget":
                return AgentDecision(
                    decision_type=DecisionType.MEMORY,
                    memory_action="forget",
                    memory_key=initial_intent.memory_key,
                    response=(
                        f"I'll forget "
                        f"{initial_intent.memory_key}."
                    ),
                )

        if context is not None:
            entity_decision = self._entity_reference_decision(
                text,
                context,
            )

            if entity_decision is not None:
                return entity_decision

            memory_response = self._memory_response(
                text,
                context,
            )

            if memory_response is not None:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=memory_response,
                )

            follow_up_response = self._conversation_response(
                text,
                context,
            )

            if follow_up_response is not None:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=follow_up_response,
                )

        intent = self._intent_resolver.resolve(user_input)

        if intent.intent_type == IntentType.CALCULATION:
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": intent.expression or "",
                },
            )

        if intent.intent_type == IntentType.MEMORY:
            if intent.memory_action == "remember":
                return AgentDecision(
                    decision_type=DecisionType.MEMORY,
                    memory_action="remember",
                    memory_key=intent.memory_key,
                    memory_value=intent.memory_value,
                    response=(
                        f"I'll remember that "
                        f"{intent.memory_key} is "
                        f"{intent.memory_value}."
                    ),
                )

            if intent.memory_action == "forget":
                return AgentDecision(
                    decision_type=DecisionType.MEMORY,
                    memory_action="forget",
                    memory_key=intent.memory_key,
                    response=(
                        f"I'll forget "
                        f"{intent.memory_key}."
                    ),
                )

        if intent.intent_type == IntentType.GREETING:
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
            previous_user_message = (
                self._previous_user_message(context)
            )

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
            previous_user_message = (
                self._previous_user_message(context)
            )

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
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} + {match.group(1)}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:subtract|minus)\s+(-?\d+(?:\.\d+)?)"
            r"\s+(?:from\s+)?it\b",
            text,
        )

        if match:
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} - {match.group(1)}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:multiply|times)\s+it\s+by\s+"
            r"(-?\d+(?:\.\d+)?)\b",
            text,
        )

        if match:
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} * {match.group(1)}"
                    ),
                },
            )

        match = re.search(
            r"\b(?:divide)\s+it\s+by\s+"
            r"(-?\d+(?:\.\d+)?)\b",
            text,
        )

        if match:
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": (
                        f"{previous_result} / {match.group(1)}"
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

        contextual_reference = (
            self._context_resolver.resolve(
                text,
                context,
            )
        )

        if contextual_reference is not None:
            return contextual_reference

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

        previous_user_message = (
            self._previous_user_message(context)
        )

        return previous_user_message

    def _previous_user_message(
        self,
        context: ContextSnapshot,
    ) -> str | None:
        for message in reversed(
            context.recent_messages[:-1]
        ):
            if message.get("role") != "user":
                continue

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

        # Match the requested memory key against the question.
        question = re.sub(
            r"^(what is my|what's my|what do i|what did i|"
            r"do you remember|remember my)\s+",
            "",
            text,
        ).strip()

        question = re.sub(
            r"\?$",
            "",
            question,
        ).strip()

        # Prefer an exact key match. ContextEngine already provides
        # memories ordered by most recently updated.
        for memory in context.memories:
            if memory.key.lower().strip() == question:
                return memory.value

        # Fallback to the strongest key match.
        question_words = set(
            re.findall(r"[a-z0-9]+", question)
        )

        best_memory = None
        best_score = 0

        for memory in context.memories:
            key_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    memory.key.lower(),
                )
            )

            score = len(question_words & key_words)

            if memory.value and score > best_score:
                best_score = score
                best_memory = memory

        if best_memory is not None:
            return best_memory.value

        return None

