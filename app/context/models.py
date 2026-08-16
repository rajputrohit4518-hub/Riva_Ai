from dataclasses import dataclass, field

from app.memory.models import Memory


@dataclass
class ContextSnapshot:
    session_id: str
    recent_messages: list[dict] = field(default_factory=list)
    memories: list[Memory] = field(default_factory=list)
