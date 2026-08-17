from app.intent.models import IntentType, ParsedIntent


class IntentResolver:
    """Classifies basic user requests before decision-making."""

    def resolve(self, user_input: str) -> ParsedIntent:
        text = user_input.strip().lower()

        if not text:
            return ParsedIntent(
                IntentType.UNKNOWN,
                confidence=0.0,
            )

        if self._is_greeting(text):
            return ParsedIntent(IntentType.GREETING)

        if text.startswith("calculate "):
            return ParsedIntent(
                IntentType.CALCULATION,
                expression=user_input.strip()[10:].strip(),
            )

        if any(
            phrase in text
            for phrase in (
                "what is my",
                "what's my",
                "what do i",
                "do you remember",
                "remember my",
            )
        ):
            return ParsedIntent(IntentType.MEMORY)

        if any(
            phrase in text
            for phrase in (
                "tell me more",
                "tell me about",
                "explain this",
                "explain that",
                "why is this",
                "why is that",
            )
        ):
            return ParsedIntent(IntentType.CONVERSATION)

        return ParsedIntent(IntentType.UNKNOWN)

    def _is_greeting(self, text: str) -> bool:
        greetings = (
            "hello",
            "hi",
            "hey",
        )

        words = text.split()

        if not words:
            return False

        if words[0] in greetings:
            return True

        return False
