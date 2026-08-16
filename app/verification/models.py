from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    reason: str


@dataclass(frozen=True)
class CorrectionResult:
    success: bool
    attempts: int
    outputs: list[str]
    error: str | None = None
