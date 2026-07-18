"""Shared step-execution + failure-classification logic for the Epic C harness.

Used by selectors.py (C1 baseline capture), break_matrix.py (C2 probe), and
replay.py (C3 record/replay) so all three exercise the *same* flow, the same
way, against real (or replayed) Playwright pages.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PWTimeoutError

from schemas import Error, ErrorKind, Step

# Tight enough that Swag Labs' buggy users actually manifest as failures
# instead of just being slow-but-technically-fine under Playwright's generous
# default timeouts — matches what a realistically-generated script would use.
ACTION_TIMEOUT_MS = 3000
GOTO_TIMEOUT_MS = 8000
SLOW_STEP_THRESHOLD_S = 1.5  # step succeeded but took this long -> flag as suspiciously slow


@dataclass
class StepOutcome:
    step_index: int
    step: Step
    ok: bool
    duration_s: float
    note: str = ""


@dataclass
class FlowOutcome:
    steps: list[StepOutcome] = field(default_factory=list)
    error: Optional[Error] = None

    @property
    def status(self) -> str:
        return "pass" if self.error is None else "fail"


def _fill_placeholders(value: str, context: dict[str, str]) -> str:
    return value.format(**context) if "{" in value else value


def run_flow(page: Page, steps: list[Step], context: dict[str, str]) -> FlowOutcome:
    """Execute every step in order; stop and classify on the first failure."""
    outcome = FlowOutcome()
    for i, step in enumerate(steps):
        start = time.monotonic()
        try:
            _execute_one(page, step, context)
            duration = time.monotonic() - start
            note = "slow" if duration > SLOW_STEP_THRESHOLD_S else ""
            outcome.steps.append(StepOutcome(i, step, True, duration, note))
        except PWTimeoutError as exc:
            duration = time.monotonic() - start
            next_step = steps[i + 1] if i + 1 < len(steps) else None
            kind, note = _classify_timeout(page, step, next_step)
            message = str(exc).splitlines()[0] + note
            outcome.steps.append(StepOutcome(i, step, False, duration, message))
            outcome.error = Error(kind=kind, message=message, step_index=i)
            return outcome
        except Exception as exc:  # noqa: BLE001 - best-effort classification, real detail in .message
            duration = time.monotonic() - start
            message = str(exc).splitlines()[0]
            outcome.steps.append(StepOutcome(i, step, False, duration, message))
            outcome.error = Error(kind="missing_element", message=message, step_index=i)
            return outcome
    return outcome


def _execute_one(page: Page, step: Step, context: dict[str, str]) -> None:
    value = _fill_placeholders(step.value, context)
    if step.action == "goto":
        page.goto(value, timeout=GOTO_TIMEOUT_MS)
    elif step.action == "fill":
        page.fill(step.selector, value, timeout=ACTION_TIMEOUT_MS)
    elif step.action == "click":
        page.click(step.selector, timeout=ACTION_TIMEOUT_MS)
    elif step.action in ("assert_visible", "expect_visible"):
        # expect_visible is agents/discovery.py's catalog vocabulary; same semantics.
        page.locator(step.selector).first.wait_for(state="visible", timeout=ACTION_TIMEOUT_MS)
    elif step.action == "select":
        page.select_option(step.selector, value, timeout=ACTION_TIMEOUT_MS)
    elif step.action == "assert_text":
        locator = page.locator(step.selector).first
        locator.wait_for(state="visible", timeout=ACTION_TIMEOUT_MS)
        actual = (locator.text_content(timeout=ACTION_TIMEOUT_MS) or "").strip()
        if actual != value.strip():
            raise AssertionError(f"expected text {value!r} at {step.selector!r}, got {actual!r}")
    else:
        raise ValueError(f"unknown step action: {step.action!r}")


# Grace window given to a *second look* after the initial action timeout fires,
# so a mid-navigation snapshot (element momentarily detached while a slow page
# repaints) isn't mistaken for a genuinely-missing selector.
GRACE_TIMEOUT_MS = 5000


def _classify_timeout(page: Page, step: Step, next_step: Optional[Step]) -> tuple[ErrorKind, str]:
    """A Playwright timeout fired on `step` — figure out why.

    Priority order, each checked live on the page (never assumed from docs):
    1. Swag Labs' own `[data-test="error"]` banner is visible -> a validation/auth
       block stopped us, so the expected next element is genuinely *missing*
       for that reason, not because a selector was renamed.
    2. The action's own effect shows up shortly after (checked via `next_step`'s
       selector when the failing step was a click/fill that should cause
       navigation — the clicked element itself may already be detached from a
       fresh DOM after navigation, so re-checking *that same* selector would be
       a false negative) -> the page was just slow (timeout), not broken.
    3. Neither happened even after a generous grace window -> the selector is
       genuinely gone (renamed/removed).
    """
    try:
        banner = page.locator('[data-test="error"]').first
        if banner.is_visible():
            return "missing_element", f" (page shows an error banner: {banner.text_content()!r})"
    except Exception:  # noqa: BLE001
        pass

    candidates = [s for s in (next_step.selector if next_step else None, step.selector) if s]
    for selector in candidates:
        try:
            page.locator(selector).first.wait_for(state="attached", timeout=GRACE_TIMEOUT_MS)
            return "timeout", ""  # forward progress happened -> just slow, not missing
        except PWTimeoutError:
            continue
    return "selector", ""  # never attached anywhere we'd expect, even with grace
