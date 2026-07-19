"""Execution node (D3) — Engine pair · branch feat/engine_core.

Runs a generated Playwright script against the target URL and captures
artifacts plus structured errors. Deterministic, no LLM.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from schemas import AgentState, Error, RunResult

LOGGER = logging.getLogger("engine_core")
LOGGER.setLevel(logging.INFO)
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[ENGINE_CORE] %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)


def _artifact_dir(state: AgentState) -> Path:
    base = Path("artifacts") / "engine_core"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _artifact_stem(state: AgentState) -> str:
    """Unique per-case, per-attempt name so evidence never overwrites.

    Includes the target user (pulled from the flow's login step) and the attempt
    number (0 = initial run, 1+ = after each repair), giving before/after evidence.
    """
    user = "unknown_user"
    if state.flow is not None:
        for step in state.flow.steps:
            if step.selector == '[data-test="username"]' and step.value:
                user = step.value
                break
    attempt = len(state.repair_attempts)  # 0 before any repair, N after N repairs
    flow_id = state.flow.id if state.flow else "flow"

    # Same flow + same user but a different `?break=` mode (e.g. test_website's cases)
    # would otherwise collide on one stem and overwrite each other's evidence.
    break_suffix = ""
    if state.flow is not None:
        break_mode = parse_qs(urlparse(state.flow.target_url).query).get("break", [None])[0]
        if break_mode:
            break_suffix = f"__{break_mode}"

    return f"{flow_id}__{user}{break_suffix}__attempt{attempt}"


def _classify_error(exc: Exception) -> tuple[str, int]:
    message = str(exc).lower()
    if "waiting for locator" in message or "strict mode" in message or "no node found" in message:
        return "missing_element", 0
    if "timeout" in message:
        return "timeout", 0
    return "selector", 0


def _dump_live_tokens(page) -> str:
    """Best-effort snapshot of what's actually on the page right now.

    On a genuine DOM change (a real site rename, not a synthetic corrupted-selector
    string) diagnosis/repair otherwise see only the failing selector and never learn
    what replaced it. Appending the live token set to logs gives the healing loop a
    real chance to find the renamed element instead of guessing blind.
    """
    try:
        tokens = sorted(set(page.eval_on_selector_all(
            "[data-test]", "els => els.map(e => e.getAttribute('data-test'))"
        )))
        return "live data-test attributes currently on page: " + ", ".join(tokens)
    except Exception as dump_exc:  # pragma: no cover - best effort only
        return f"(could not read live data-test attributes: {dump_exc})"


def _safe_screenshot(page, path: Path) -> None:
    """Capture the page even on failure so the UI has a real 'broken' image.

    Best-effort: the page may be mid-failure, so never raise.
    """
    try:
        page.screenshot(path=str(path))
    except Exception:  # pragma: no cover - page may already be in a bad state
        pass


def _finish(state: AgentState, result: RunResult) -> AgentState:
    """Attach `result` as the run's current result, and — if this execution is the
    re-run that follows a repair attempt — backfill that attempt's own `result` too.

    `repair_node` appends a `RepairAttempt` with `result=None`, documented there as
    "filled in by the execution node after re-run", but nothing previously did that.
    Left unfilled, `state.repair_attempts[-1].result` stayed None forever, which (a)
    hid every repair attempt's screenshot from the gallery — only the single latest
    `state.result` screenshot ever rendered, so the UI never showed the before/after
    healing evidence — and (b) kept the pipeline view's Repair node stuck on "ACTIVE"
    even after a genuine pass, since that view keys off `last_attempt.result`.

    Also stashes the very first result as `state.original_result` (set once, never
    overwritten). Without this, once healing succeeds `state.result` is replaced by
    the final PASS and the original failure's screenshot/error is gone — the UI can
    no longer show "what broke" after it's fixed.
    """
    if state.original_result is None:
        state.original_result = result
    state.result = result
    if state.repair_attempts and state.repair_attempts[-1].result is None:
        state.repair_attempts[-1].result = result
    return state


def execution_node(state: AgentState) -> AgentState:
    assert state.script is not None
    assert state.flow is not None

    artifact_dir = _artifact_dir(state)
    stem = _artifact_stem(state)
    screenshot_path = artifact_dir / f"{stem}.png"
    trace_path = artifact_dir / f"{stem}.zip"

    try:
        namespace: dict[str, Any] = {}
        exec(compile(state.script.code, "<generated>", "exec"), namespace)
        run_fn = namespace.get("run")
        if not callable(run_fn):
            raise ValueError("generated script must define a callable run(page)")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                run_fn(page)
                page.screenshot(path=str(screenshot_path))
            except PlaywrightError as exc:
                kind, step_index = _classify_error(exc)
                _safe_screenshot(page, screenshot_path)  # capture the broken page
                _finish(state, RunResult(
                    script_id=state.script.flow_id,
                    status="fail",
                    logs=f"{exc}\n\n{_dump_live_tokens(page)}",
                    screenshots=[str(screenshot_path)],
                    trace=str(trace_path),
                    error=Error(kind=kind, message=str(exc), step_index=step_index),
                ))
                browser.close()
                return state
            except Exception as exc:  # pragma: no cover - defensive fallback
                _safe_screenshot(page, screenshot_path)  # capture the broken page
                _finish(state, RunResult(
                    script_id=state.script.flow_id,
                    status="fail",
                    logs=f"{exc}\n\n{_dump_live_tokens(page)}",
                    screenshots=[str(screenshot_path)],
                    trace=str(trace_path),
                    error=Error(kind="flow_change", message=str(exc), step_index=-1),
                ))
                browser.close()
                return state
            finally:
                try:
                    browser.close()
                except Exception:
                    pass

        _finish(state, RunResult(
            script_id=state.script.flow_id,
            status="pass",
            logs="execution completed",
            screenshots=[str(screenshot_path)],
            trace=str(trace_path),
        ))
        return state
    except Exception as exc:  # pragma: no cover - defensive fallback
        LOGGER.exception("engine_core execution failed")
        _finish(state, RunResult(
            script_id=state.script.flow_id,
            status="fail",
            logs=str(exc),
            screenshots=[str(screenshot_path)] if 'screenshot_path' in locals() else [],
            error=Error(kind="timeout", message=str(exc), step_index=-1),
        ))
        return state
