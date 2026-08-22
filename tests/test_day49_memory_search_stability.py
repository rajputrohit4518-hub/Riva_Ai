from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(
        store=MemoryStore(":memory:")
    )


def test_search_returns_results_in_deterministic_order():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite language two",
        "Python",
        "preference",
    )

    first = memory.search("favorite")
    second = memory.search("favorite")

    assert first == second


def test_exact_key_match_remains_first_after_repeated_search():
    memory = build_memory()

    memory.remember(
        "Rust",
        "systems language",
        "programming",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    for _ in range(5):
        results = memory.search("Rust")

        assert len(results) == 2
        assert results[0].key == "Rust"
        assert results[1].key == "favorite language"
        assert results[1].value == "Rust"


def test_search_does_not_mutate_memory_data():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    before = memory.recall("favorite language")

    results = memory.search("Rust")

    after = memory.recall("favorite language")

    assert results
    assert before is not None
    assert after is not None

    assert after.key == before.key
    assert after.value == before.value
    assert after.category == before.category
    assert after.created_at == before.created_at
    assert after.updated_at == before.updated_at


def test_search_limit_zero_returns_empty():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.search("name", limit=0) == []


def test_search_limit_one_returns_best_result():
    memory = build_memory()

    memory.remember(
        "Rust",
        "systems language",
        "programming",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search(
        "Rust",
        limit=1,
    )

    assert len(results) == 1
    assert results[0].key == "Rust"
    

def test_search_is_case_insensitive_for_value():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("RUST")

    assert len(results) == 1
    assert results[0].value == "Rust"


def test_search_is_case_insensitive_for_category():
    memory = build_memory()

    memory.remember(
        "coding",
        "Rust",
        "programming",
    )

    results = memory.search("PROGRAMMING")

    assert len(results) == 1
    assert results[0].category == "programming"


def test_search_ignores_single_character_query_words():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    results = memory.search("a")

    assert results == []


def test_search_handles_whitespace_query():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.search("   ") == []


def test_search_respects_requested_limit():
    memory = build_memory()

    memory.remember(
        "language one",
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


def test_search_preserves_latest_updated_memory():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Python",
        "preference",
    )

    memory.remember(
        "Rust",
        "systems language",
        "programming",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    stored = memory.recall("favorite language")

    assert stored is not None
    assert stored.value == "Rust"
    assert stored.category == "preference"

    results = memory.search("Rust")

    assert len(results) == 2
    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"
