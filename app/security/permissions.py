from app.security.models import (
    PermissionDecision,
    PermissionPolicy,
    RiskLevel,
)


class PermissionEngine:
    def __init__(self) -> None:
        self._policies = {
            RiskLevel.LOW: PermissionPolicy(
                risk_level=RiskLevel.LOW,
                decision=PermissionDecision.ALLOW,
            ),
            RiskLevel.MEDIUM: PermissionPolicy(
                risk_level=RiskLevel.MEDIUM,
                decision=PermissionDecision.CONFIRM,
            ),
            RiskLevel.HIGH: PermissionPolicy(
                risk_level=RiskLevel.HIGH,
                decision=PermissionDecision.CONFIRM,
            ),
            RiskLevel.CRITICAL: PermissionPolicy(
                risk_level=RiskLevel.CRITICAL,
                decision=PermissionDecision.DENY,
            ),
        }

    def evaluate(self, risk_level: str) -> PermissionDecision:
        try:
            level = RiskLevel(risk_level)
        except ValueError as exc:
            raise ValueError(
                f"Unknown risk level: {risk_level}"
            ) from exc

        return self._policies[level].decision
