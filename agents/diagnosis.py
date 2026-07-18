"""Error Diagnosis agent (E1) — Healing pair · branch feat/healing_loop.

Classifies + explains the 4 failure classes. Reasoning tier.
"""
from __future__ import annotations

from schemas import AgentState, Diagnosis


def diagnosis_node(state: AgentState) -> AgentState:
    # TODO(Healing): call model_for("diagnosis") on state.result.error + logs/screenshots.
    assert state.result is not None and state.result.error is not None
    err = state.result.error
    state.diagnosis = Diagnosis(
        error=err,
        root_cause=f"stub: {err.kind} at step {err.step_index}",
        confidence=0.5,
        suggested_fix="stub fix",
    )
    return state
