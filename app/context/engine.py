from app.context.models import ContextSnapshot
from app.memory.manager import MemoryManager
from app.core.session import RivaSession


class ContextEngine:
    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
    ) -> None:
        self._memory = memory_manager or MemoryManager()

    def build(
        self,
        session: RivaSession,
        query: str,
        memory_limit: int = 5,
    ) -> ContextSnapshot:

        memories = self._memory.search(
            query=query,
            limit=memory_limit,
        )

        return ContextSnapshot(
            session_id=session.session_id,
            recent_messages=session.history(),
            memories=memories,
        )
