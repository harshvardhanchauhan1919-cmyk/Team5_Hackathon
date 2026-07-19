"""C2 — the break-user matrix: empirically verify which Swag Labs buggy user
triggers which failure class. Run it, don't trust the docs.

Run:  python -m harness.break_matrix
Writes harness/break_matrix.yaml + a screenshot per user under
harness/fixtures/break_matrix/ as evidence.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

from credentials import PASSWORD, USERS
from harness.selectors import CHECKOUT_FLOW
from harness.step_executor import run_flow
from schemas import ErrorKind

OUT_YAML = Path(__file__).parent / "break_matrix.yaml"
EVIDENCE_DIR = Path(__file__).parent / "fixtures" / "break_matrix"


def probe_user(user: str, headless: bool = True) -> dict:
    """Run CHECKOUT_FLOW as `user`, capture what actually happens (not what the docs claim)."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    shot_path = EVIDENCE_DIR / f"{user}.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        context = {"username": user, "password": PASSWORD}
        outcome = run_flow(page, CHECKOUT_FLOW.steps, context)
        page.screenshot(path=str(shot_path))
        browser.close()

    if outcome.error is None:
        return {
            "user": user,
            "observed_kind": None,
            "message": "flow completed end-to-end with no observed failure",
            "failed_step": None,
            "failed_step_description": None,
            "evidence": str(shot_path),
        }
    return {
        "user": user,
        "observed_kind": outcome.error.kind,
        "message": outcome.error.message,
        "failed_step": outcome.error.step_index,
        "failed_step_description": CHECKOUT_FLOW.steps[outcome.error.step_index].description,
        "evidence": str(shot_path),
    }


def run_matrix(headless: bool = True) -> dict[str, dict]:
    results = {}
    for user in USERS:
        print(f"[break-matrix] probing {user} ...")
        results[user] = probe_user(user, headless=headless)
        kind = results[user]["observed_kind"] or "pass"
        print(f"[break-matrix] {user} -> {kind}")
    return results


def get_expected_error(user: str) -> ErrorKind | None:
    """Typed lookup for Diagnosis / harness consumers: what this user is known to produce."""
    data = yaml.safe_load(OUT_YAML.read_text(encoding="utf-8"))
    return data.get(user, {}).get("observed_kind")


if __name__ == "__main__":
    results = run_matrix()
    OUT_YAML.write_text(yaml.safe_dump(results, sort_keys=False), encoding="utf-8")
    print(f"\nwrote {OUT_YAML}")
    for user, r in results.items():
        print(f"  {user:26s} -> {r['observed_kind'] or 'pass'}")
