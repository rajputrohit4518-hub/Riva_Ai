from enum import Enum

from pydantic import BaseModel, Field


class BrainDecisionType(str, Enum):
    RESPOND = "respond"
    TOOL = "tool"


class BrainDecision(BaseModel):
    decision_type: BrainDecisionType
    response: str | None = None
    tool_name: str | None = None
    tool_arguments: dict = Field(default_factory=dict)
    reasoning_summary: str = ""
