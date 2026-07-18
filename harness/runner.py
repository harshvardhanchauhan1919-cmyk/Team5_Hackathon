"""F1 — harness runner over {flow x break} cases (Epic F, the proof).

Drives the same pipeline shape as graph.build.build_graph() — Discovery ->
ScriptGen -> Execution -> (pass|give_up|diagnose -> Diagnosis -> Repair ->
Execution) — once per case, and calls harness.verify (F3) on every case the
pipeline reports as healed.

Why this doesn't just import graph.build.build_graph(): tools/execution.py is
Engine's file (D3) and currently hardcodes `status="pass"` as a placeholder
(see its own TODO). Importing it as-is would make every case here trivially
pass and the scoreboard meaningless. This module wires an equivalent graph
locally with a *real* Playwright execution node (reusing harness.step_executor,
the same logic C1-C3 already proved against the live site), so the harness has
a genuine signal today. Once D3 lands the real execution node, delete
`_make_real_execution_node` and `build_harness_graph` and call
`graph.build.build_graph()` directly instead — `run_case`/`run_all` don't need
to change.

Run:  python -m harness.runner
"""
from __future__ import annotations

import json
from pathlib import Path

from langgraph.graph import END, StateGraph
from playwright.sync_api import sync_playwright

from agents.diagnosis import diagnosis_node
from agents.discovery import discovery_node
from agents.repair import repair_node
from agents.script_gen import script_gen_node
from harness.cases import Case, load_cases
from harness.step_executor import run_flow
from harness.verify import verify_healed_live
from schemas import AgentState, RunResult

REPORT_PATH = Path(__file__).parent / "report.json"


def _make_real_execution_node(headless: bool = True):
    """A real (non-stub) execution node: runs state.flow.steps via Playwright
    and classifies failures with the same logic harness.break_matrix uses."""

    def _execution_node(state: AgentState) -> AgentState:
        assert state.flow is not None, "discovery must run first"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            outcome = run_flow(page, state.flow.steps, context={})
            browser.close()
        state.result = RunResult(
            script_id=state.script.flow_id if state.script else state.flow.id,
            status=outcome.status,
            logs="; ".join(s.note for s in outcome.steps if s.note) or "ok",
            error=outcome.error,
        )
        return state

    return _execution_node


def _after_execution(state: AgentState) -> str:
    if state.result and state.result.status == "pass":
        return "done"
    if len(state.repair_attempts) >= state.max_attempts:
        return "give_up"
    return "diagnose"


def build_harness_graph(headless: bool = True):
    """Mirrors graph.build.build_graph()'s wiring; see module docstring for why."""
    execution_node = _make_real_execution_node(headless=headless)
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
    g.add_edge("repair", "execution")
    return g.compile()


def run_case(app, case: Case, headless: bool = True) -> dict:
    # discovery_node picks the flow/user/url from `config`, not from a pre-seeded
    # state.flow (see agents/discovery.py) — so the case is passed as config here.
    final = app.invoke(AgentState(), config=case.config())
    # LangGraph returns a dict-like state; normalise as hello_langgraph.py does.
    final_state = final if isinstance(final, AgentState) else AgentState(**final)

    result = final_state.result
    assert result is not None, "execution always sets state.result"
    healed = bool(final_state.repair_attempts) and result.status == "pass"

    verified = None
    verify_reason = None
    if healed:
        v = verify_healed_live(final_state, headless=headless)
        verified, verify_reason = v.verified, v.reason

    return {
        "case_id": case.id,
        "user": case.user,
        "expected_kind": case.expected_kind,
        "initial_status": "pass" if not final_state.repair_attempts and result.status == "pass"
        else "fail",
        "final_status": result.status,
        "repair_attempt_count": len(final_state.repair_attempts),
        "healed": healed,
        "verified_healed": verified,
        "verify_reason": verify_reason,
        "final_error_kind": result.error.kind if result.error else None,
        "final_error_message": result.error.message if result.error else None,
    }


def run_all(headless: bool = True) -> list[dict]:
    app = build_harness_graph(headless=headless)
    results = []
    for case in load_cases():
        print(f"[runner] running {case.id} ...")
        r = run_case(app, case, headless=headless)
        results.append(r)
        print(
            f"[runner] {case.id}: initial={r['initial_status']} final={r['final_status']} "
            f"healed={r['healed']} verified={r['verified_healed']}"
        )
    return results


if __name__ == "__main__":
    results = run_all()
    REPORT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {REPORT_PATH}")
