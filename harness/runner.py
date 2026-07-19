"""F1 — harness runner over {flow x break} cases (Epic F, the proof).

Drives the real pipeline (graph.build.build_graph(): Discovery -> ScriptGen ->
Execution -> (pass|give_up|diagnose -> Diagnosis -> Repair -> Execution)) once
per case, and calls harness.verify's verify_healed_live (F3) on every case the
pipeline reports as healed.

Note: Diagnosis/Repair now call the real model_for("diagnosis"/"repair"),
which hits OpenRouter for real unless USE_MOCK=1 is set in the environment —
set it before running this against every buggy case if you don't want to
burn credits / need network access.

Run:  python -m harness.runner
"""
from __future__ import annotations

import json
from pathlib import Path

from graph.build import build_graph
from harness.cases import Case, load_cases
from harness.verify import verify_healed_live
from schemas import AgentState

REPORT_PATH = Path(__file__).parent / "report.json"


def run_case(app, case: Case, headless: bool = True) -> dict:
    # discovery_node picks the flow/user/url from `config`, not from a pre-seeded
    # state.flow (see agents/discovery.py) — so the case is passed as config here.
    final = app.invoke(AgentState(), config=case.config())
    # LangGraph returns a dict-like state; normalise as main.py does.
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
        "screenshots": result.screenshots,  # evidence: artifacts/engine_core/*.png
        "trace": result.trace,              # evidence: open with `playwright show-trace`
    }


def run_all(headless: bool = True) -> list[dict]:
    app = build_graph()
    results = []
    for case in load_cases():
        print(f"[runner] running {case.id} ...")
        r = run_case(app, case, headless=headless)
        results.append(r)
        print(f"[runner] {case.id}: initial={r['initial_status']} -> {_verdict(r)}")
    return results


def _verdict(r: dict) -> str:
    """One unambiguous outcome per case. 'healed' alone is the naive pipeline flag;
    only a verified heal is a genuine win. A healed-but-unverified case is a FALSE
    HEAL that F3 caught (e.g. the model switched credentials instead of fixing the
    script)."""
    if r["initial_status"] == "pass":
        return "BASELINE PASS (nothing to heal)"
    if r["healed"] and r["verified_healed"]:
        return "HEALED (verified by F3)"
    if r["healed"] and not r["verified_healed"]:
        return f"FALSE HEAL - rejected by F3: {r['verify_reason']}"
    return "NOT HEALED"


if __name__ == "__main__":
    results = run_all()
    REPORT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {REPORT_PATH}")
