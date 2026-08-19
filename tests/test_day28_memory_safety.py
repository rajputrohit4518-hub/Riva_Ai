from app.memory.policy import MemoryAction
from app.memory.safety import MemorySafetyPolicy


def test_day28_safe_memory_allowed():
    decision = MemorySafetyPolicy().evaluate(
        "favorite_language",
        "Python",
        "preference",
    )
    assert decision.action == MemoryAction.REMEMBER


def test_day28_password_blocked():
    decision = MemorySafetyPolicy().evaluate(
        "password",
        "secret123",
    )
    assert decision.action == MemoryAction.IGNORE


def test_day28_api_key_blocked():
    decision = MemorySafetyPolicy().evaluate(
        "my api key",
        "abc123",
    )
    assert decision.action == MemoryAction.IGNORE


def test_day28_financial_category_blocked():
    decision = MemorySafetyPolicy().evaluate(
        "account",
        "12345",
        "financial",
    )
    assert decision.action == MemoryAction.IGNORE
