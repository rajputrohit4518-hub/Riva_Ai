from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Memory:
    key: str
    value: str
    category: str = "general"
    created_at: datetime | None = None
    updated_at: datetime | None = None
