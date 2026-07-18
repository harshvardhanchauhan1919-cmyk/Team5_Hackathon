"""Assemble the self-healing pipeline as a LangGraph StateGraph (B2).

Discovery -> ScriptGen -> Execution -> (pass -> END | fail -> Diagnosis -> Repair -> Execution)
Repair loops up to state.max_attempts, then gives up.
Human-in-the-loop: gate the Repair->Execution edge when state.hitl is True (LangGraph interrupt).
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from agents.diagnosis import diagnosis_node
from agents.discovery import discovery_node
from agents.repair import repair_node
from agents.script_gen import script_gen_node
from schemas import AgentState
from tools.execution import execution_node


def _after_execution(state: AgentState) -> str:
    if state.result and state.result.status == "pass":
        return "done"
    if len(state.repair_attempts) >= state.max_attempts:
        return "give_up"
    return "diagnose"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("discovery", discovery_node)
    g.add_node("script_gen", script_gen_node)
    g.add_node("execution", execution_node)
    g.add_node("diagnosis", diagnosis_node)
    g.add_node("repair", repair_node)

    g.set_entry_point("discovery")
    g.add_edge("discovery", "script_gen")
    g.add_edge("script_gen", "execution")
    g.add_conditional_edges(
        "execution",
        _after_execution,
        {"done": END, "give_up": END, "diagnose": "diagnosis"},
    )
    g.add_edge("diagnosis", "repair")
    g.add_edge("repair", "execution")  # TODO(Healing): add interrupt() here when state.hitl
    return g.compile()
