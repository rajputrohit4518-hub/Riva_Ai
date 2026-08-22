from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(
        store=MemoryStore(":memory:")
    )


def test_exact_key_match_ranks_first():
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


def test_key_match_beats_value_match():
    memory = build_memory()

    memory.remember(
        "Rust language",
        "systems programming",
        "programming",
    )

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 2
    assert results[0].key == "Rust language"


def test_key_match_beats_category_match():
    memory = build_memory()

    memory.remember(
        "programming",
        "Rust",
        "general",
    )

    memory.remember(
        "coding preference",
        "Python",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 2
    assert results[0].key == "programming"


def test_exact_key_match_beats_partial_key_match():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite language preference",
        "Python",
        "preference",
    )

    results = memory.search("favorite language")

    assert len(results) == 2
    assert results[0].key == "favorite language"


def test_multiple_key_words_rank_higher():
    memory = build_memory()

    memory.remember(
        "favorite programming language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite language",
        "Python",
        "preference",
    )

    results = memory.search(
        "favorite programming language"
    )

    assert len(results) == 2
    assert results[0].key == "favorite programming language"


def test_key_match_is_case_insensitive():
    memory = build_memory()

    memory.remember(
        "Favorite Language",
        "Rust",
        "preference",
    )

    results = memory.search("favorite language")

    assert len(results) == 1
    assert results[0].key == "Favorite Language"
    assert results[0].value == "Rust"


def test_value_match_still_returns_memory():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 1
    assert results[0].value == "Rust"


def test_category_match_still_returns_memory():
    memory = build_memory()

    memory.remember(
        "coding",
        "Rust",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 1
    assert results[0].category == "programming"


def test_relevant_memory_ranks_above_unrelated_memory():
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

    results = memory.search("favorite language")

    assert results[0].key == "favorite language"


def test_search_limit_applies_after_ranking():
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

    memory.remember(
        "Rust tools",
        "Cargo",
        "programming",
    )

    results = memory.search(
        "Rust",
        limit=2,
    )

    assert len(results) == 2
    assert results[0].key == "Rust"


def test_update_keeps_updated_memory_ranked_correctly():
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

    results = memory.search("Rust")

    assert len(results) == 2
    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"
    assert results[1].key == "Rust"


def test_search_preserves_memory_metadata_after_ranking():
    memory = build_memory()

    memory.remember(
        "Rust",
        "systems programming language",
        "programming",
    )

    results = memory.search("Rust")

    assert len(results) == 1

    result = results[0]

    assert result.key == "Rust"
    assert result.value == "systems programming language"
    assert result.category == "programming"
    assert result.created_at is not None
    assert result.updated_at is not None
