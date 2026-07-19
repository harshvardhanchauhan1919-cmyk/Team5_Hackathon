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
    by independently re-running the REPAIRED SCRIPT (state.script.code) in a fresh
    browser — not the original flow steps.

    Why the repaired script and not state.flow.steps: Repair rewrites state.script;
    verifying state.flow.steps would re-test the *original* (still-broken) flow and
    never confirm the actual fix. We verify what was repaired.

    Checks, in order:
    1. At least one repair attempt happened — a "pass" with zero repairs was never
       broken, so it can't have been healed.
    2. The reported result really is "pass".
    3. There is a repaired script that defines a callable run(page).
    4. A completely fresh re-run of that repaired script still passes — catches a
       one-off flake or a cached "pass".
    """
    if not state.repair_attempts:
        return VerifyResult(False, "no repair attempts recorded — nothing was actually healed")
    if state.result is None or state.result.status != "pass":
        reported = state.result.status if state.result else None
        return VerifyResult(False, f"reported status is {reported!r}, not pass")
    if state.script is None:
        return VerifyResult(False, "no repaired script on final state to re-verify")

    # Guard against the "credential switch" cheat. A genuine heal fixes the SCRIPT for
    # the SAME login user. If the repaired script no longer logs in as the original
    # user (e.g. the model swapped a locked-out account for standard_user just to make
    # it pass), that's sidestepping the failure, not healing it.
    original_user = next(
        (s.value for s in (state.flow.steps if state.flow else [])
         if s.selector == '[data-test="username"]' and s.value),
        None,
    )
    if original_user and original_user not in state.script.code:
        return VerifyResult(
            False,
            f"repaired script no longer logs in as {original_user!r} — "
            "credential switch, not a genuine script heal",
        )

    namespace: dict = {}
    try:
        exec(compile(state.script.code, "<verify>", "exec"), namespace)
    except Exception as exc:  # noqa: BLE001
        return VerifyResult(False, f"repaired script failed to compile: {exc}")
    run_fn = namespace.get("run")
    if not callable(run_fn):
        return VerifyResult(False, "repaired script defines no callable run(page)")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            run_fn(page)
        except Exception as exc:  # noqa: BLE001
            browser.close()
            return VerifyResult(False, f"independent re-run of repaired script failed: {exc}")
        browser.close()

    return VerifyResult(True, "independent re-run of the repaired script reproduced a full pass")
