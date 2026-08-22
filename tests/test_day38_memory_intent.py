from app.intent.models import IntentType
from app.intent.resolver import IntentResolver


def test_day38_remember_command():
    intent = IntentResolver().resolve(
        "remember my name is Rohit"
    )

    assert intent.intent_type == IntentType.MEMORY
    assert intent.memory_action == "remember"
    assert intent.memory_key == "name"
    assert intent.memory_value == "Rohit"


def test_day38_forget_command():
    intent = IntentResolver().resolve(
        "forget my name"
    )

    assert intent.intent_type == IntentType.MEMORY
    assert intent.memory_action == "forget"
    assert intent.memory_key == "name"


def test_day38_existing_calculation_still_works():
    intent = IntentResolver().resolve("25 * 6")

    assert intent.intent_type == IntentType.CALCULATION
    assert intent.expression == "25 * 6"
