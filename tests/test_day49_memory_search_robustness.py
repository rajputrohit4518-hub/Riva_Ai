from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(
        store=MemoryStore(":memory:")
    )


def test_search_empty_query_returns_no_results():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.search("") == []


def test_search_whitespace_query_returns_no_results():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.search("   ") == []


def test_search_is_case_insensitive():
    memory = build_memory()

    memory.remember(
        "Favorite Language",
        "Rust",
        "preference",
    )

    results = memory.search("favorite language")

    assert len(results) == 1
    assert results[0].key == "Favorite Language"


def test_search_ignores_single_character_tokens():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("a favorite")

    assert len(results) == 1
    assert results[0].key == "favorite language"


def test_search_limit_zero_returns_no_results():
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
        "favorite language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite food",
        "Pizza",
        "preference",
    )

    results = memory.search(
        "favorite language",
        limit=1,
    )

    assert len(results) == 1
    assert results[0].key == "favorite language"


def test_search_returns_empty_for_unmatched_query():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.search("completely unrelated") == []


def test_search_preserves_category():
    memory = build_memory()

    memory.remember(
        "coding",
        "Rust",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 1
    assert results[0].category == "programming"


def test_search_preserves_value():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 1
    assert results[0].value == "Rust"


def test_search_after_update_returns_latest_value():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Python",
        "preference",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("favorite language")

    assert len(results) == 1
    assert results[0].value == "Rust"


def test_search_after_delete_returns_no_results():
    memory = build_memory()

    memory.remember(
        "name",
        "Rohit",
        "identity",
    )

    memory.forget("name")

    assert memory.search("name") == []


def test_search_does_not_duplicate_same_memory():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search(
        "favorite language Rust preference"
    )

    assert len(results) == 1
    assert results[0].key == "favorite language"
