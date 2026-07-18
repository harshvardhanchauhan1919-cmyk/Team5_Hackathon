"""Adaptive Repair agent (E2) — Healing pair · branch feat/healing_loop.

Rewrites the script from the diagnosis. Reasoning tier. Attempt-capped by state.max_attempts.
Human-in-the-loop gate lives on the edge out of this node (see graph/build.py).

TODO(Healing → Engine): add interrupt() on the repair→execution edge in graph/build.py
when state.hitl is True so the human can review the repaired script before re-run.
"""
from __future__ import annotations

import logging

from agents.repair_prompt import REPAIR_SYSTEM_PROMPT
from schemas import AgentState, RepairAttempt, Script

logger = logging.getLogger(__name__)

# Maximum length of previous-attempt history injected into the prompt (characters).
_MAX_HISTORY_CHARS = 2000


def repair_node(state: AgentState) -> AgentState:
    """LangGraph node: take the Diagnosis and rewrite the Script."""
    assert state.diagnosis is not None, "repair_node called with no diagnosis in state"
    assert state.script is not None, "repair_node called with no script in state"

    attempt_no = len(state.repair_attempts) + 1
    diag = state.diagnosis

    # ------------------------------------------------------------------
    # Build the user-turn prompt.
    # ------------------------------------------------------------------
    history_section = _format_history(state.repair_attempts)

    user_prompt = (
        f"## Diagnosis\n"
        f"Error kind: {diag.error.kind}\n"
        f"Root cause: {diag.root_cause}\n"
        f"Confidence: {diag.confidence:.2f}\n"
        f"Suggested fix: {diag.suggested_fix}\n\n"
        f"## Current (broken) script\n"
        f"```python\n{state.script.code}\n```\n\n"
        f"{history_section}"
        f"Repair attempt #{attempt_no}. "
        f"Return ONLY the corrected Python script — no explanations."
    )

    # ------------------------------------------------------------------
    # Call the model.
    # ------------------------------------------------------------------
    from config import model_for  # deferred to avoid circular import

    model = model_for("repair")

    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=REPAIR_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    try:
        response = model.invoke(messages)
        new_code = _clean_script(response.content)
        logger.info("Repair attempt #%d produced %d chars of code.", attempt_no, len(new_code))
    except Exception as exc:  # noqa: BLE001
        # Fallback: keep original code but mark it as "attempted".
        logger.warning("Repair model error (%s) — falling back to original script.", exc)
        new_code = state.script.code + f"\n# repair attempt {attempt_no} failed: {exc}"

    # ------------------------------------------------------------------
    # Update state.
    # ------------------------------------------------------------------
    new_script = Script(flow_id=state.script.flow_id, code=new_code)
    state.repair_attempts.append(
        RepairAttempt(
            diagnosis=diag,
            new_script=new_script,
            attempt_no=attempt_no,
            result=None,  # filled in by the execution node after re-run
        )
    )
    state.script = new_script
    return state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_script(raw: str) -> str:
    """Strip markdown fences and leading/trailing whitespace from LLM output."""
    lines = raw.strip().splitlines()
    # Remove ```python / ``` wrappers if the model added them despite instructions.
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _format_history(attempts: list[RepairAttempt]) -> str:
    """Summarise previous repair attempts for the prompt (capped at _MAX_HISTORY_CHARS)."""
    if not attempts:
        return ""
    parts = ["## Previous repair attempts (do NOT repeat these changes)\n"]
    for a in attempts:
        entry = (
            f"Attempt #{a.attempt_no}: "
            f"result={a.result.status if a.result else 'pending'}\n"
            f"Script snippet (first 300 chars):\n{a.new_script.code[:300]}\n\n"
        )
        parts.append(entry)
    full = "".join(parts)
    if len(full) > _MAX_HISTORY_CHARS:
        full = full[:_MAX_HISTORY_CHARS] + "\n...(history truncated)\n\n"
    return full
