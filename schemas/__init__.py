"""Shared typed contract — FREEZE THIS FIRST (B1).

Every agent is a node: def node(state) -> state.
No changes without a team call. This is the single hard gate of the build.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

ErrorKind = Literal["selector", "timeout", "missing_element", "flow_change"]
RunStatus = Literal["pass", "fail", "pending"]


class Step(BaseModel):
    action: str                      # e.g. "goto", "fill", "click"
    selector: str = ""               # data-test string, e.g. [data-test="username"]
    value: str = ""                  # text to type, url to visit, etc.
    description: str = ""


class Flow(BaseModel):
    id: str
    name: str
    steps: list[Step] = Field(default_factory=list)
    target_url: str


class Script(BaseModel):
    flow_id: str
    code: str                        # generated Playwright script (Python)


class Error(BaseModel):
    kind: ErrorKind
    message: str
    step_index: int = -1


class RunResult(BaseModel):
    script_id: str
    status: RunStatus = "pending"
    logs: str = ""
    screenshots: list[str] = Field(default_factory=list)
    video: Optional[str] = None
    trace: Optional[str] = None
    error: Optional[Error] = None


class Diagnosis(BaseModel):
    error: Error
    root_cause: str
    confidence: float = 0.0
    suggested_fix: str = ""


class RepairAttempt(BaseModel):
    diagnosis: Diagnosis
    new_script: Script
    attempt_no: int
    result: Optional[RunResult] = None


class AgentState(BaseModel):
    """The object that flows through the LangGraph graph."""
    flow: Optional[Flow] = None
    script: Optional[Script] = None
    result: Optional[RunResult] = None
    diagnosis: Optional[Diagnosis] = None
    repair_attempts: list[RepairAttempt] = Field(default_factory=list)
    max_attempts: int = 3            # give-up-after-N
    hitl: bool = False               # human-in-the-loop gate on the repair step
