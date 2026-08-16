from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


@dataclass
class ExecutionResult:
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    tool_name: str = ""
    status: ExecutionStatus = ExecutionStatus.FAILED
    result: Any = None
    error: str | None = None
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

    def complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc)
