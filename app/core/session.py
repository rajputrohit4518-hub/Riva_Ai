from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RivaSession:
    session_id: str

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    command_count: int = 0

    messages: list[dict[str, Any]] = field(
        default_factory=list
    )

    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        if not role:
            raise ValueError(
                "Message role cannot be empty."
            )

        if not content:
            raise ValueError(
                "Message content cannot be empty."
            )

        self.messages.append({
            "role": role,
            "content": content,
        })

    def history(self) -> list[dict[str, Any]]:
        return list(self.messages)
