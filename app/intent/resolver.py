import re

from app.intent.models import IntentType, ParsedIntent


class IntentResolver:
    """Classifies basic user requests before decision-making."""

    _ARITHMETIC_PATTERN = re.compile(
        r"^\s*[-+*/().\d\s]+\s*$"
    )

    _REMEMBER_PATTERN = re.compile(
        r"^\s*remember\s+(?:that\s+)?"
        r"(?:my\s+)?(.+?)\s+is\s+(.+?)\s*$",
        re.IGNORECASE,
    )

    _FORGET_PATTERN = re.compile(
        r"^\s*forget\s+(?:my\s+)?(.+?)\s*$",
        re.IGNORECASE,
    )

    def resolve(self, user_input: str) -> ParsedIntent:
        text = user_input.strip().lower()

        if not text:
            return ParsedIntent(
                IntentType.UNKNOWN,
                confidence=0.0,
            )

        remember_match = self._REMEMBER_PATTERN.match(
            user_input.strip()
        )

        if remember_match:
            return ParsedIntent(
                IntentType.MEMORY,
                memory_key=remember_match.group(1).strip(),
                memory_value=remember_match.group(2).strip(),
                memory_action="remember",
            )

        forget_match = self._FORGET_PATTERN.match(
            user_input.strip()
        )

        if forget_match:
            return ParsedIntent(
                IntentType.MEMORY,
                memory_key=forget_match.group(1).strip(),
                memory_action="forget",
            )

        if self._is_greeting(text):
            return ParsedIntent(IntentType.GREETING)

        if text.startswith("calculate "):
            return ParsedIntent(
                IntentType.CALCULATION,
                expression=user_input.strip()[10:].strip(),
            )

        if self._is_bare_arithmetic(text):
            return ParsedIntent(
                IntentType.CALCULATION,
                expression=user_input.strip(),
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

    def _is_bare_arithmetic(self, text: str) -> bool:
        if not any(
            operator in text
            for operator in ("+", "-", "*", "/")
        ):
            return False

        return bool(self._ARITHMETIC_PATTERN.fullmatch(text))

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
