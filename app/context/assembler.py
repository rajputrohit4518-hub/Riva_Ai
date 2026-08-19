from app.context.engine import ContextEngine
from app.memory.manager import MemoryManager


class ContextAssembler:
    def __init__(self, memory_manager=None, context_engine=None):
        self._memory = memory_manager or MemoryManager()
        self._context = context_engine or ContextEngine(self._memory)

    def build(self, session, query: str):
        query = query.strip()
        if not query:
            raise ValueError("Context query cannot be empty.")

        return self._context.build(
            session=session,
            query=query,
        )
