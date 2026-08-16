from app.planner.executor import PlanExecutor
from app.planner.models import ExecutionPlan
from app.verification.models import (
    CorrectionResult,
    VerificationStatus,
)
from app.verification.verifier import ResultVerifier


class SelfCorrector:
    def __init__(
        self,
        executor: PlanExecutor,
        verifier: ResultVerifier | None = None,
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        self._executor = executor
        self._verifier = verifier or ResultVerifier()
        self._max_attempts = max_attempts

    def run(
        self,
        plan: ExecutionPlan,
    ) -> CorrectionResult:

        outputs: list[str] = []
        last_error: str | None = None

        for attempt in range(1, self._max_attempts + 1):

            result = self._executor.execute(plan)

            outputs.extend(result.outputs)

            if not result.success:
                last_error = result.error
                continue

            final_output = (
                result.outputs[-1]
                if result.outputs
                else None
            )

            verification = self._verifier.verify(
                final_output
            )

            if (
                verification.status
                == VerificationStatus.PASSED
            ):
                return CorrectionResult(
                    success=True,
                    attempts=attempt,
                    outputs=outputs,
                )

            last_error = verification.reason

        return CorrectionResult(
            success=False,
            attempts=self._max_attempts,
            outputs=outputs,
            error=last_error,
        )
