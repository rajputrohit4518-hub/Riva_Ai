from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlanStepType(str, Enum):
    TOOL = "tool"
    RESPOND = "respond"
    VERIFY = "verify"


@dataclass(frozen=True)
class PlanStep:
    tool_name: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    step_id: str = "step_1"
    step_type: PlanStepType = PlanStepType.TOOL
    description: str = ""


@dataclass(frozen=True)
class ExecutionPlan:
    goal: str
    steps: tuple[PlanStep, ...] | list[PlanStep] = field(
        default_factory=tuple
    )

    @property
    def is_empty(self) -> bool:
        return not self.steps
