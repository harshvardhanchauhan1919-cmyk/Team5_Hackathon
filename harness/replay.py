"""C3 — HAR recording + deterministic replay, so CI and the recorded demo
never depend on the live Swag Labs site being up or unchanged.

Record:  python -m harness.replay record
Verify:  python -m harness.replay verify   (replays every HAR, diffs the
         resulting classification against break_matrix.yaml)
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from harness.break_matrix import PASSWORD, USERS, get_expected_error
from harness.selectors import CHECKOUT_FLOW
from harness.step_executor import FlowOutcome, run_flow

HAR_DIR = Path(__file__).parent / "fixtures" / "har"


def har_path_for(user: str) -> Path:
    return HAR_DIR / f"checkout_{user}.har"


def record_har(user: str, headless: bool = True) -> Path:
    HAR_DIR.mkdir(parents=True, exist_ok=True)
    path = har_path_for(user)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(record_har_path=str(path), record_har_mode="full")
        page = ctx.new_page()
        run_flow(page, CHECKOUT_FLOW.steps, {"username": user, "password": PASSWORD})
        ctx.close()  # flushes the HAR to disk
        browser.close()
    return path


def replay_from_har(user: str, headless: bool = True) -> FlowOutcome:
    """Replay `user`'s recorded HAR fully offline (no live network calls).

    Note: closing a route_from_har context can print benign
    `asyncio.CancelledError` traceback noise from Playwright's own internal
    route teardown (an unmatched resource still in flight when the context
    closes). Cosmetic only — doesn't affect the returned outcome.
    """
    path = har_path_for(user)
    if not path.exists():
        raise FileNotFoundError(f"no HAR recorded for {user!r} — run `record` first: {path}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context()
        ctx.route_from_har(str(path), url="**/*", not_found="abort")
        page = ctx.new_page()
        outcome = run_flow(page, CHECKOUT_FLOW.steps, {"username": user, "password": PASSWORD})
        page.wait_for_timeout(250)  # let any in-flight route_from_har lookups settle before closing
        ctx.close()
        browser.close()
    return outcome


def record_all(headless: bool = True) -> None:
    for user in USERS:
        print(f"[replay] recording {user} ...")
        record_har(user, headless=headless)
    print(f"recorded {len(USERS)} HAR files -> {HAR_DIR}")


def verify_all(headless: bool = True) -> bool:
    """Replay every recorded HAR; confirm it reproduces break_matrix.yaml's classification."""
    all_ok = True
    for user in USERS:
        outcome = replay_from_har(user, headless=headless)
        observed = outcome.error.kind if outcome.error else None
        expected = get_expected_error(user)
        ok = observed == expected
        all_ok = all_ok and ok
        status = "OK" if ok else "MISMATCH"
        print(
            f"[replay] {user}: replay={observed or 'pass'} "
            f"expected={expected or 'pass'} -> {status}"
        )
    return all_ok


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "record"
    if cmd == "record":
        record_all()
    elif cmd == "verify":
        ok = verify_all()
        sys.exit(0 if ok else 1)
    else:
        print("usage: python -m harness.replay [record|verify]")
        sys.exit(2)
