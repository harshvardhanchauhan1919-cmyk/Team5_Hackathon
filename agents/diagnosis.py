"""Error Diagnosis agent (E1) — Healing pair · branch feat/healing_loop.

Classifies + explains the 4 failure classes:
  selector | timeout | missing_element | flow_change

Uses model_for("diagnosis") — reasoning tier (Claude Sonnet) in prod,
FakeModel in dev/CI (USE_MOCK=1).
"""
from __future__ import annotations

import json
import logging

from agents.diagnosis_prompt import DIAGNOSIS_SYSTEM_PROMPT
from schemas import AgentState, Diagnosis

logger = logging.getLogger(__name__)


def diagnosis_node(state: AgentState) -> AgentState:
    """LangGraph node: read the failed RunResult and produce a Diagnosis."""
    assert state.result is not None and state.result.error is not None, (
        "diagnosis_node called with no error in state.result"
    )

    err = state.result.error

    # ------------------------------------------------------------------
    # Build the user-turn prompt from the available run context.
    # ------------------------------------------------------------------
    screenshot_note = (
        f"Screenshots captured: {', '.join(state.result.screenshots)}"
        if state.result.screenshots
        else "No screenshots captured."
    )
    log_tail = "\n".join(state.result.logs.splitlines()[-10:]) if state.result.logs else "(no logs)"

    user_prompt = (
        f"Error: kind={err.kind}, message={err.message!r}, step_index={err.step_index}\n"
        f"Logs (last 10 lines):\n{log_tail}\n"
        f"{screenshot_note}\n\n"
        "Diagnose this failure and respond with JSON only."
    )

    # ------------------------------------------------------------------
    # Call the model (real or mock, depending on USE_MOCK env var).
    # ------------------------------------------------------------------
    from config import model_for  # imported here to avoid circular imports at module load

    model = model_for("diagnosis")

    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=DIAGNOSIS_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    try:
        response = model.invoke(messages)
        raw = response.content.strip()
        # Strip markdown json code block fences if the LLM output includes them
        if raw.startswith("```"):
            lines = raw.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw = "\n".join(lines).strip()
        
        data = json.loads(raw)
        state.diagnosis = Diagnosis(
            error=err,
            root_cause=data.get("root_cause", f"Unknown root cause for {err.kind}"),
            confidence=float(data.get("confidence", 0.5)),
            suggested_fix=data.get("suggested_fix", ""),
        )
        logger.info(
            "Diagnosis: %s (confidence=%.2f)",
            state.diagnosis.root_cause,
            state.diagnosis.confidence,
        )
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        # Graceful fallback — keep the pipeline running even if the model misfires.
        logger.warning("Diagnosis parse error (%s) — using fallback stub.", exc)
        state.diagnosis = Diagnosis(
            error=err,
            root_cause=f"Could not parse diagnosis for {err.kind} at step {err.step_index}.",
            confidence=0.0,
            suggested_fix="Manual inspection required.",
        )

    return state
