from app.context.assembler import ContextAssembler


def test_context_assembler_builds_context(tmp_path):
    from app.core.session import RivaSession
    from app.memory.manager import MemoryManager
    from app.memory.store import MemoryStore

    memory = MemoryManager(
        store=MemoryStore(":memory:")
    )
    assembler = ContextAssembler(memory_manager=memory)
    session = RivaSession(session_id="day27-context")

    session.add_message("user", "My preferred language is Python.")

    context = assembler.build(
        session=session,
        query="What is my preferred language?",
    )

    assert context is not None


def test_context_assembler_rejects_empty_query(tmp_path):
    assembler = ContextAssembler()

    from app.core.session import RivaSession

    try:
        assembler.build(
            session=RivaSession(session_id="day27-empty"),
            query="   ",
        )
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
