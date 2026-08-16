from app.brain.models import BrainDecision, BrainDecisionType
from app.tools.registry import ToolRegistry


class BrainGateway:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def validate(
        self,
        decision: BrainDecision,
    ) -> BrainDecision:

        if decision.decision_type == BrainDecisionType.RESPOND:
            if not decision.response or not decision.response.strip():
                raise ValueError(
                    "Response decision requires response text."
                )

            return decision

        if decision.decision_type == BrainDecisionType.TOOL:
            if not decision.tool_name:
                raise ValueError(
                    "Tool decision requires a tool name."
                )

            try:
                self._registry.get(decision.tool_name)
            except KeyError as exc:
                raise ValueError(
                    f"Unknown tool: {decision.tool_name}"
                ) from exc

            if decision.response:
                raise ValueError(
                    "Tool decisions cannot contain response text."
                )

            return decision

        raise ValueError(
            f"Unsupported brain decision: "
            f"{decision.decision_type}"
        )
