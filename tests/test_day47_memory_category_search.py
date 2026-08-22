from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(
        store=MemoryStore(":memory:")
    )


def test_search_can_match_memory_category():
    memory = build_memory()

    memory.remember(
        "coding",
        "Rust",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 1
    assert results[0].key == "coding"
    assert results[0].value == "Rust"
    assert results[0].category == "programming"


def test_search_can_match_memory_value():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 1
    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"


def test_search_prefers_key_match_over_value_match():
    memory = build_memory()

    memory.remember(
        "Rust",
        "programming language",
        "programming",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 2
    assert results[0].key == "Rust"


def test_search_returns_category_and_value_together():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search(
        "favorite language preference"
    )

    assert len(results) == 1
    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"
    assert results[0].category == "preference"


def test_search_respects_limit():
    memory = build_memory()

    memory.remember(
        "language",
        "Rust",
        "programming",
    )

    memory.remember(
        "language two",
        "Python",
        "programming",
    )

    memory.remember(
        "language three",
        "Go",
        "programming",
    )

    results = memory.search(
        "programming",
        limit=2,
    )

    assert len(results) == 2


def test_unknown_category_is_normalized():
    memory = build_memory()

    memory.remember(
        "test",
        "value",
        "unknown-category",
    )

    stored = memory.recall("test")

    assert stored is not None
    assert stored.category == "general"


def test_category_retrieval_survives_update():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Python",
        "preference",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "programming",
    )

    stored = memory.recall("favorite language")

    assert stored is not None
    assert stored.value == "Rust"
    assert stored.category == "programming"


def test_list_memories_returns_latest_category():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    memories = memory.list_memories()

    assert len(memories) == 2

    assert any(
        item.key == "name"
        and item.category == "identity"
        for item in memories
    )

    assert any(
        item.key == "favorite language"
        and item.category == "preference"
        for item in memories
    )
