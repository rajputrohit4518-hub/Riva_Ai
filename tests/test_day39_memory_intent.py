from app.intent.models import IntentType
from app.intent.resolver import IntentResolver


def test_remember_command_is_memory_intent():
    intent = IntentResolver().resolve(
        "remember my name is Rohit"
    )

    assert intent.intent_type == IntentType.MEMORY


def test_forget_command_is_memory_intent():
    intent = IntentResolver().resolve(
        "forget my name"
    )

    assert intent.intent_type == IntentType.MEMORY


def test_memory_question_is_memory_intent():
    intent = IntentResolver().resolve(
        "what is my name"
    )

    assert intent.intent_type == IntentType.MEMORY
