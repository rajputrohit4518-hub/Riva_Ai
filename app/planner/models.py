from dataclasses import dataclass, field
from enum import Enum


class PlanStepType(str, Enum):
    TOOL = "tool"
    RESPOND = "respond"
    VERIFY = "verify"


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    step_type: PlanStepType
    description: str
    tool_name: str | None = None
    arguments: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]
