from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    execution_id: str
    tool_name: str
    status: str
    result: Any = None
    error: str | None = None


class AuditLogger:
    def __init__(self, path: str = "logs/riva_audit.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: AuditEvent) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(asdict(event), default=str)
                + "\n"
            )

    def create_event(
        self,
        execution_id: str,
        tool_name: str,
        status: str,
        result: Any = None,
        error: str | None = None,
    ) -> AuditEvent:
        return AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_id=execution_id,
            tool_name=tool_name,
            status=status,
            result=result,
            error=error,
        )
