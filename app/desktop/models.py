from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopApplication:
    name: str
    executable: str


@dataclass(frozen=True)
class DesktopActionResult:
    success: bool
    application: str
    message: str
    pid: int | None = None
