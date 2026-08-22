from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))


def test_equal_relevance_has_deterministic_order():
    memory = build_memory()

    memory.remember("alpha", "Rust", "programming")
    memory.remember("beta", "Rust", "programming")

    results = memory.search("Rust")

    assert len(results) == 2
    assert results[0].key == "beta"
    assert results[1].key == "alpha"


def test_repeated_search_preserves_order():
    memory = build_memory()

    memory.remember("alpha", "Rust", "programming")
    memory.remember("beta", "Rust", "programming")
    memory.remember("gamma", "Rust", "programming")

    expected = [item.key for item in memory.search("Rust")]

    for _ in range(10):
        assert [item.key for item in memory.search("Rust")] == expected


def test_limit_applies_after_ranking():
    memory = build_memory()

    memory.remember("alpha", "Rust", "programming")
    memory.remember("beta", "Rust", "programming")
    memory.remember("gamma", "Rust", "programming")

    results = memory.search("Rust", limit=2)

    assert len(results) == 2
    assert [item.key for item in results] == ["gamma", "beta"]


def test_exact_key_still_beats_value_match():
    memory = build_memory()

    memory.remember("Rust", "systems language", "programming")
    memory.remember("favorite language", "Rust", "preference")

    results = memory.search("Rust")

    assert results[0].key == "Rust"
    assert results[1].key == "favorite language"


def test_updated_preference_value_still_ranks_correctly():
    memory = build_memory()

    memory.remember("Rust", "systems language", "programming")
    memory.remember("favorite language", "Python", "preference")
    memory.remember("favorite language", "Rust", "preference")

    results = memory.search("Rust")

    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"


def test_search_preserves_metadata():
    memory = build_memory()

    memory.remember("favorite language", "Rust", "preference")

    before = memory.recall("favorite language")
    memory.search("Rust")
    after = memory.recall("favorite language")

    assert before is not None
    assert after is not None
    assert after.created_at == before.created_at
    assert after.updated_at == before.updated_at
    assert after.value == before.value
    assert after.category == before.category
