"""Run one pipeline case and print compact JSON evidence."""
from __future__ import annotations

import argparse
import json

from graph.build import build_graph
from harness.cases import SELECTOR_BREAK_CASE, Case, load_cases
from harness.test_website_cases import load_test_website_cases
from harness.verify import verify_healed_live
from schemas import AgentState


def _case(name: str) -> Case:
    if name == "baseline":
        return Case(
            id="e2e_checkout__baseline",
            user="standard_user",
            expected_kind=None,
            flow_id="e2e_checkout",
        )
    if name == "selector-break":
        return SELECTOR_BREAK_CASE
    for case in load_cases():
        if case.id == name:
            return case
    for case in load_test_website_cases():
        if case.id == name:
            return case
    raise ValueError(f"unknown case {name!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    case = _case(args.case)
    app = build_graph()
    final = app.invoke(AgentState(), config=case.config())
    state = final if isinstance(final, AgentState) else AgentState(**final)

    verified = None
    verify_reason = None
    if args.verify and state.repair_attempts:
        verification = verify_healed_live(state)
        verified = verification.verified
        verify_reason = verification.reason

    result = state.result
    print(json.dumps(
        {
            "case_id": case.id,
            "flow": state.flow.id if state.flow else None,
            "user": case.user,
            "status": result.status if result else None,
            "error": result.error.model_dump() if result and result.error else None,
            "screenshots": result.screenshots if result else [],
            "trace": result.trace if result else None,
            "repair_attempts": len(state.repair_attempts),
            "verified_healed": verified,
            "verify_reason": verify_reason,
            "script_preview": state.script.code[:500] if state.script else None,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
