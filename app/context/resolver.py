import re

from app.context.models import ContextSnapshot


class ContextResolver:
    """Resolves references in the current user input against conversation context."""

    def resolve(
        self,
        text: str,
        context: ContextSnapshot,
    ) -> str | None:
        if len(context.recent_messages) < 2:
            return None

        if self._is_contextual_reference(text):
            return self._find_relevant_previous_user_message(context)

        return None

    def _is_contextual_reference(self, text: str) -> bool:
        explicit_reference = any(
            re.search(pattern, text)
            for pattern in (
                r"\bits\b",
                r"\bthat\b",
                r"\bthis\b",
                r"\bthe above\b",
                r"\bthe previous\b",
            )
        )

        topic_reference = any(
            phrase in text
            for phrase in (
                "tell me more about the project",
                "tell me about the project",
                "tell me more about this",
                "tell me more about that",
                "can you explain that",
                "can you explain this",
                "explain that",
                "explain this",
                "why is that important",
                "why is this important",
                "why is that",
                "why is this",
                "what are its goals",
                "when is the meeting",
                "when is the project",
                "what is the project",
                "what is the meeting",
                "what are the project",
                "what are the meeting",
            )
        )

        contextual_question = any(
            phrase in text
            for phrase in (
                "tell me more",
                "tell me about",
            )
        )

        possessive_reference = bool(
            re.search(
                r"\bwhat are its\b",
                text,
            )
        )

        return (
            explicit_reference
            or topic_reference
            or possessive_reference
            or contextual_question
        )

    def _find_relevant_previous_user_message(
        self,
        context: ContextSnapshot,
    ) -> str | None:
        messages = context.recent_messages[:-1]

        for message in reversed(messages):
            if message.get("role") != "user":
                continue

            content = str(
                message.get("content", "")
            ).strip()

            if not content:
                continue

            return content

        return None
