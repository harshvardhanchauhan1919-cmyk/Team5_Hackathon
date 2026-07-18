"""Execution node (D3) — Engine pair · branch feat/engine_core.

Runs the Playwright script and captures artifacts. Deterministic, no LLM.
"""
from __future__ import annotations

from schemas import AgentState, RunResult


def execution_node(state: AgentState) -> AgentState:
    # TODO(Engine): actually exec the script via Playwright, capture screenshots/video/trace.
    assert state.script is not None
    state.result = RunResult(script_id=state.script.flow_id, status="pass", logs="stub run")
    return state
