from app.verification.models import (
    VerificationResult,
    VerificationStatus,
)


class ResultVerifier:
    def verify(
        self,
        result: str | None,
    ) -> VerificationResult:

        if result is None:
            return VerificationResult(
                status=VerificationStatus.FAILED,
                reason="No result was produced.",
            )

        if not str(result).strip():
            return VerificationResult(
                status=VerificationStatus.FAILED,
                reason="Result was empty.",
            )

        return VerificationResult(
            status=VerificationStatus.PASSED,
            reason="Result contains usable output.",
        )
