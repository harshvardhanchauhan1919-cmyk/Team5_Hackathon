"""Script Generator agent (D2) — Generation pair · branch feat/discovery_agent.

Turns a Flow into a runnable Playwright script.
"""
from __future__ import annotations

from schemas import AgentState, Script


def script_gen_node(state: AgentState) -> AgentState:
    # TODO(Generation): call model_for("script_gen") to generate real code from state.flow.
    assert state.flow is not None, "discovery must run first"
    state.script = Script(flow_id=state.flow.id, code="# generated Playwright script goes here")
    return state
