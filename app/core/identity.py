from dataclasses import dataclass


@dataclass(frozen=True)
class RivaIdentity:
    name: str = "Riva"
    version: str = "0.1.0"
    role: str = "Personal AI Assistant"


IDENTITY = RivaIdentity()
