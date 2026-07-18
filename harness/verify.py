"""F3 — "healed is truly healed" verification (Epic F, the proof).

A repair that passes for the wrong reason is a demo-killer. This module
re-checks any case the pipeline reported as "healed" before F2's scoreboard
is allowed to count it as a win.

Note on scope: this file is Scoreboard's (F3), coordinate with Healing before
adding anything here — they also touch this file for their half of F3 per
BRANCH_OWNERSHIP.md.
"""
from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import sync_playwright

from harness.selectors import CHECKOUT_FLOW
from harness.step_executor import run_flow
from schemas import AgentState


@dataclass
class VerifyResult:
    verified: bool
    reason: str


def verify_healed(state: AgentState, headless: bool = True) -> VerifyResult:
    """Given a final AgentState the pipeline reported as "healed", double-check it.

    Checks, in order:
    1. At least one repair attempt actually happened — a "pass" with zero
       repair attempts was never broken, so it can't have been healed.
    2. The reported result really is "pass".
    3. A completely fresh re-run (new browser context, not the cached
       RunResult) still passes — catches a one-off flake reported as healed.
    4. That fresh re-run actually completes as many steps as the C1 baseline —
       catches a "pass" that quietly short-circuited instead of truly fixing
       the flow.
    """
    if not state.repair_attempts:
        return VerifyResult(False, "no repair attempts recorded — nothing was actually healed")
    if state.result is None or state.result.status != "pass":
        reported = state.result.status if state.result else None
        return VerifyResult(False, f"reported status is {reported!r}, not pass")
    if state.flow is None:
        return VerifyResult(False, "no flow on final state to re-verify against")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        outcome = run_flow(page, state.flow.steps, context={})
        browser.close()

    if outcome.status != "pass":
        return VerifyResult(False, f"independent re-run failed: {outcome.error}")
    if len(outcome.steps) < len(CHECKOUT_FLOW.steps):
        return VerifyResult(
            False,
            f"independent re-run only completed {len(outcome.steps)}/"
            f"{len(CHECKOUT_FLOW.steps)} baseline steps — looks short-circuited",
        )
    return VerifyResult(True, "independent re-run reproduced a full pass")
