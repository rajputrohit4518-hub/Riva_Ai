from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_search_handles_mixed_whitespace():
    m=build_memory()
    m.remember("favorite language","Rust","preference")
    r=m.search("  FaVoRiTe\t  language  ")
    assert len(r)==1
    assert r[0].key=="favorite language"

def test_search_handles_newlines():
    m=build_memory()
    m.remember("favorite language","Rust","preference")
    assert m.search("favorite\nlanguage")[0].key=="favorite language"

def test_search_none_is_safe():
    m=build_memory()
    assert m.search(None)==[]

def test_search_limit_is_preserved():
    m=build_memory()
    for k in ("a","b","c"):
        m.remember(k,"Rust","programming")
    assert len(m.search("Rust",limit=2))==2
