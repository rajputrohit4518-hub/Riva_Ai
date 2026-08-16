from dataclasses import dataclass, field


@dataclass
class RuntimeResult:
    session_id: str
    user_input: str
    response: str = ""
    tool_outputs: list[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None
