"""One clear entry point — Engine pair · branch feat/engine_core.

Runs the self-healing pipeline once: Discovery -> ScriptGen -> Execution ->
(pass | Diagnosis -> Repair -> re-run, capped at max_attempts).

Usage:
    python main.py
Exit code is 0 on a passing/healed run, 1 otherwise, so it's CI-friendly.
"""
from __future__ import annotations

import logging
import sys

from graph.build import build_graph
from schemas import AgentState

LOGGER = logging.getLogger("engine_core")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[ENGINE_CORE] %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


def _as_state(final) -> AgentState:
    """LangGraph may return a dict-like state; normalise to AgentState."""
    if isinstance(final, AgentState):
        return final
    if isinstance(final, dict):
        return AgentState(**final)
    return final


def run() -> AgentState:
    LOGGER.info("building graph")
    app = build_graph()
    LOGGER.info("invoking pipeline")
    final = _as_state(app.invoke(AgentState()))

    result = final.result
    attempts = len(final.repair_attempts)
    status = result.status if result else "unknown"

    LOGGER.info("pipeline finished: status=%s repair_attempts=%d", status, attempts)
    if result:
        for shot in result.screenshots:
            LOGGER.info("artifact: screenshot=%s", shot)
        if result.trace:
            LOGGER.info("artifact: trace=%s", result.trace)
        if result.error:
            LOGGER.info("last error: kind=%s message=%s", result.error.kind, result.error.message)

    return final


def main() -> int:
    final = run()
    result = final.result
    healed = result is not None and result.status == "pass" and len(final.repair_attempts) > 0
    if healed:
        print("pipeline complete: HEALED after", len(final.repair_attempts), "repair attempt(s)")
    elif result is not None and result.status == "pass":
        print("pipeline complete: PASS")
    else:
        print("pipeline complete: FAIL", "-", result.error.kind if result and result.error else "no result")
    return 0 if (result is not None and result.status == "pass") else 1


if __name__ == "__main__":
    sys.exit(main())
