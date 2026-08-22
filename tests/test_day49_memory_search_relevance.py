from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(
        store=MemoryStore(":memory:")
    )


def test_exact_key_match_has_highest_relevance():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite food",
        "language is important",
        "general",
    )

    results = memory.search("favorite language")

    assert len(results) == 2
    assert results[0].key == "favorite language"


def test_key_match_ranks_above_value_match():
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


def test_key_match_ranks_above_category_match():
    memory = build_memory()

    memory.remember(
        "programming language",
        "Rust",
        "programming",
    )

    memory.remember(
        "coding",
        "Python",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 2
    assert results[0].key == "programming language"


def test_exact_multi_word_key_match_ranks_first():
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


def test_partial_key_match_ranks_below_exact_key_match():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    memory.remember(
        "favorite programming language",
        "Python",
        "preference",
    )

    results = memory.search("favorite language")

    assert len(results) == 2
    assert results[0].key == "favorite language"


def test_relevance_is_case_insensitive():
    memory = build_memory()

    memory.remember(
        "Favorite Language",
        "Rust",
        "preference",
    )

    results = memory.search("FAVORITE LANGUAGE")

    assert len(results) == 1
    assert results[0].key == "Favorite Language"


def test_unrelated_memory_does_not_rank_above_relevant_memory():
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


def test_value_match_remains_searchable():
    memory = build_memory()

    memory.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = memory.search("Rust")

    assert len(results) == 1
    assert results[0].key == "favorite language"


def test_category_match_remains_searchable():
    memory = build_memory()

    memory.remember(
        "coding",
        "Rust",
        "programming",
    )

    results = memory.search("programming")

    assert len(results) == 1
    assert results[0].category == "programming"


def test_relevance_ranking_survives_memory_update():
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


def test_search_limit_is_applied_after_relevance_ranking():
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

    memory.remember(
        "Rust tools",
        "Cargo",
        "programming",
    )

    results = memory.search(
        "Rust",
        limit=1,
    )

    assert len(results) == 1
    assert results[0].key == "Rust"


def test_search_preserves_memory_metadata():
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
