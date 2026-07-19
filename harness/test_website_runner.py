"""Harness runner over the test_website case matrix (see harness/test_website_cases.py).

Mirrors harness/runner.py's shape exactly (same Case, same verify_healed_live), but
points at the local test_website target instead of saucedemo.com and writes to a
separate report file so it never clobbers harness/report.json.

Start the site first:
    cd test_website && npm run dev   # http://localhost:3000

Run (real LLM, pick a backend — see README.md "Run modes"):
    LLM_BACKEND=opencode python -m harness.test_website_runner   # no API key needed
    LLM_BACKEND=claude   python -m harness.test_website_runner   # no API key needed
    LLM_BACKEND=api      python -m harness.test_website_runner   # needs OPENROUTER_API_KEY

Run (deterministic, no LLM/network at all):
    USE_MOCK=1 python -m harness.test_website_runner
"""
from __future__ import annotations

import json
from pathlib import Path

from graph.build import build_graph
from harness.test_website_cases import Case, load_test_website_cases
from harness.verify import verify_healed_live
from schemas import AgentState

REPORT_JSON = Path(__file__).parent / "report_test_website.json"
REPORT_MD = Path(__file__).parent / "report_test_website.md"


def run_case(app, case: Case, headless: bool = True) -> dict:
    final = app.invoke(AgentState(), config=case.config())
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
        "target_url": case.target_url,
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
        "screenshots": result.screenshots,
        "trace": result.trace,
    }


def _verdict(r: dict) -> str:
    if r["initial_status"] == "pass":
        return "BASELINE PASS (nothing to heal)"
    if r["healed"] and r["verified_healed"]:
        return "HEALED (verified by F3)"
    if r["healed"] and not r["verified_healed"]:
        return f"FALSE HEAL - rejected by F3: {r['verify_reason']}"
    return "NOT HEALED"


def run_all(headless: bool = True) -> list[dict]:
    app = build_graph()
    results = []
    for case in load_test_website_cases():
        print(f"[test_website_runner] running {case.id} ...")
        r = run_case(app, case, headless=headless)
        results.append(r)
        print(f"[test_website_runner] {case.id}: initial={r['initial_status']} -> {_verdict(r)}")
    return results


def _write_report_md(results: list[dict]) -> None:
    lines = ["# test_website harness report", ""]
    lines.append("| case | expected | initial | final | attempts | verdict |")
    lines.append("|---|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['case_id']} | {r['expected_kind'] or 'pass'} | {r['initial_status']} | "
            f"{r['final_status']} | {r['repair_attempt_count']} | {_verdict(r)} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    all_results = run_all()
    REPORT_JSON.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    _write_report_md(all_results)
    print(f"\nwrote {REPORT_JSON}")
    print(f"wrote {REPORT_MD}")
