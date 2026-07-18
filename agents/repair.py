"""Adaptive Repair agent (E2) — Healing pair · branch feat/healing_loop.

Rewrites the script from the diagnosis. Reasoning tier. Attempt-capped by state.max_attempts.
Human-in-the-loop gate lives on the edge out of this node (see graph).
"""
from __future__ import annotations

from schemas import AgentState, RepairAttempt, Script


def repair_node(state: AgentState) -> AgentState:
    # TODO(Healing): call model_for("repair") using state.diagnosis to produce a new script.
    assert state.diagnosis is not None and state.script is not None
    attempt_no = len(state.repair_attempts) + 1
    new_script = Script(flow_id=state.script.flow_id, code=state.script.code + "\n# repaired")
    state.repair_attempts.append(
        RepairAttempt(diagnosis=state.diagnosis, new_script=new_script, attempt_no=attempt_no)
    )
    state.script = new_script
    return state
