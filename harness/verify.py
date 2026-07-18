""""Healed is truly healed" verification (F3) — Scoreboard + Healing.

A repair that passes for the wrong reason is a demo-killer. Two complementary
checks live here (both pairs touch this file per BRANCH_OWNERSHIP.md, so keep
them separate rather than merging the logic):

- `verify_healed(result, original_result=None)` — Healing's lightweight check:
  does this RunResult look like a clean pass? Used by tools/test_observer.py
  and the pipeline itself right after a repair attempt.
- `verify_healed_live(state, headless=True)` — Scoreboard's deeper check: an
  independent, fresh Playwright re-run (not the cached RunResult) that also
  confirms the flow wasn't short-circuited. Used by harness/runner.py before
  F2's scoreboard is allowed to count a case as healed.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import sync_playwright

from harness.selectors import CHECKOUT_FLOW
from harness.step_executor import run_flow
from schemas import AgentState, RunResult

logger = logging.getLogger(__name__)


def verify_healed(result: RunResult, original_result: Optional[RunResult] = None) -> bool:
    """Verify that a repaired execution is successful.

    Args:
        result: The RunResult of the latest execution after repair.
        original_result: The original failing RunResult before repair (optional).

    Returns:
        True if the script execution is successful and contains no errors.
    """
    if result.status != "pass":
        logger.info("Verification failed: RunResult status is %s (expected 'pass')", result.status)
        return False

    if result.error is not None:
        logger.info("Verification failed: RunResult has an error: %s", result.error.message)
        return False

    # Optional check: make sure we did not regress on some steps
    if original_result and original_result.error:
        logger.info(
            "Verification successful: Repaired execution passed. Original error was %s at step %d.",
            original_result.error.kind,
            original_result.error.step_index,
        )
    else:
        logger.info("Verification successful: Execution passed.")

    return True


@dataclass
class VerifyResult:
    verified: bool
    reason: str


def verify_healed_live(state: AgentState, headless: bool = True) -> VerifyResult:
    """Given a final AgentState the pipeline reported as "healed", double-check it
    with a fresh, independent Playwright run rather than trusting the cached RunResult.

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
