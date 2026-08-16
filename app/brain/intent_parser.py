import re

from app.brain.intent_models import (
    IntentType,
    ParsedIntent,
)


class RivaIntentParser:
    def parse(
        self,
        text: str,
    ) -> ParsedIntent:

        original = text
        normalized = text.strip().lower()

        if not normalized:
            return ParsedIntent(
                intent_type=IntentType.UNKNOWN,
                capability_name=None,
                device_type=None,
                arguments={},
                confidence=1.0,
                original_text=original,
            )

        if normalized in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good evening",
        }:
            return ParsedIntent(
                intent_type=IntentType.CONVERSATION,
                capability_name=None,
                device_type=None,
                arguments={},
                confidence=0.99,
                original_text=original,
            )

        calculator_match = re.fullmatch(
            r"(?:calculate|compute)\s+(.+)",
            normalized,
        )

        if calculator_match:
            return ParsedIntent(
                intent_type=IntentType.COMMAND,
                capability_name="calculator",
                device_type=None,
                arguments={
                    "expression":
                        calculator_match.group(1)
                },
                confidence=0.98,
                original_text=original,
            )

        if normalized in {
            "what time is it",
            "what's the time",
            "tell me the time",
        }:
            return ParsedIntent(
                intent_type=IntentType.QUERY,
                capability_name="time",
                device_type=None,
                arguments={},
                confidence=0.98,
                original_text=original,
            )

        return ParsedIntent(
            intent_type=IntentType.UNKNOWN,
            capability_name=None,
            device_type=None,
            arguments={},
            confidence=0.0,
            original_text=original,
        )
