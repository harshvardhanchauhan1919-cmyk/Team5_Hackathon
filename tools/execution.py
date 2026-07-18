"""Execution node (D3) — Engine pair · branch feat/engine_core.

Runs a generated Playwright script against the target URL and captures
artifacts plus structured errors. Deterministic, no LLM.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

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


def _run_step(page: Any, step: Any) -> None:
    action = step.action
    if action == "goto":
        page.goto(step.value, wait_until="domcontentloaded")
    elif action == "fill":
        locator = page.locator(step.selector) if step.selector else None
        if locator is None:
            raise ValueError("fill step is missing a selector")
        locator.fill(step.value)
    elif action == "click":
        locator = page.locator(step.selector) if step.selector else None
        if locator is None:
            raise ValueError("click step is missing a selector")
        locator.click()
    else:
        raise ValueError(f"unsupported action: {action}")


def execution_node(state: AgentState) -> AgentState:
    assert state.script is not None
    assert state.flow is not None

    artifact_dir = _artifact_dir(state)
    screenshot_path = artifact_dir / f"{state.flow.id}.png"
    trace_path = artifact_dir / f"{state.flow.id}.zip"
    logs: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                for step in state.flow.steps:
                    LOGGER.info("executing step %s: %s", step.action, step.description or step.selector)
                    _run_step(page, step)
                page.screenshot(path=str(screenshot_path))
                browser.close()
            except PlaywrightError as exc:
                browser.close()
                logs.append(str(exc))
                error_kind = "selector"
                if "waiting for locator" in str(exc).lower() or "strict mode" in str(exc).lower():
                    error_kind = "missing_element"
                error = Error(
                    kind=error_kind,
                    message=str(exc),
                    step_index=0,
                )
                state.result = RunResult(
                    script_id=state.script.flow_id,
                    status="fail",
                    logs="\n".join(logs),
                    screenshots=[str(screenshot_path)],
                    trace=str(trace_path),
                    error=error,
                )
                return state
            except Exception as exc:  # pragma: no cover - defensive fallback
                browser.close()
                logs.append(str(exc))
                error = Error(kind="flow_change", message=str(exc), step_index=-1)
                state.result = RunResult(
                    script_id=state.script.flow_id,
                    status="fail",
                    logs="\n".join(logs),
                    screenshots=[str(screenshot_path)],
                    trace=str(trace_path),
                    error=error,
                )
                return state

        state.result = RunResult(
            script_id=state.script.flow_id,
            status="pass",
            logs="\n".join(logs) if logs else "execution completed",
            screenshots=[str(screenshot_path)],
            trace=str(trace_path),
        )
        return state
    except Exception as exc:  # pragma: no cover - defensive fallback
        LOGGER.exception("engine_core execution failed")
        state.result = RunResult(
            script_id=state.script.flow_id,
            status="fail",
            logs=str(exc),
            screenshots=[str(screenshot_path)] if 'screenshot_path' in locals() else [],
            error=Error(kind="timeout", message=str(exc), step_index=-1),
        )
        return state
