"""F1 — the {flow x break} case matrix consumed by harness.runner.

Drives the real Discovery agent (agents.discovery.discovery_node), which as of
the discovery_agent merge selects a flow from the frozen catalog
(fixtures/flow_catalog.json) and re-points it at a given user/url via
`config={"configurable": {...}}` — it no longer respects a pre-seeded
state.flow. So a "case" here is just the config to pass to app.invoke(), not a
materialized Flow.

The break-user list + each user's expected failure class still comes from C2's
empirically-verified harness/break_matrix.yaml (computed against harness/
selectors.py's own baseline flow — near-identical to the catalog's
"e2e_checkout" since both walk the same live Swag Labs checkout).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import yaml

from harness.break_matrix import OUT_YAML as BREAK_MATRIX_YAML

DEFAULT_FLOW_ID = "e2e_checkout"
DEFAULT_TARGET_URL = "https://www.saucedemo.com/"


@dataclass
class Case:
    id: str
    user: str
    expected_kind: Optional[str]  # from C2's break matrix; None means "should pass"
    flow_id: str = DEFAULT_FLOW_ID
    target_url: str = DEFAULT_TARGET_URL
    break_selector: Optional[str] = None  # corrupt this selector (a real, healable break)

    def config(self) -> dict:
        """The RunnableConfig to pass to app.invoke() — how discovery_node picks the case."""
        configurable = {
            "flow_id": self.flow_id,
            "user": self.user,
            "target_url": self.target_url,
        }
        if self.break_selector:
            configurable["break_selector"] = self.break_selector
        return {"configurable": configurable}


# A genuine script-vs-page break (not a user break): standard_user, but one selector
# is corrupted. This is the case that truly heals — the LLM fixes the selector, and F3
# verifies by re-running the repaired script. Healable in both mock and real mode.
SELECTOR_BREAK_CASE = Case(
    id="checkout_broken_selector",
    user="standard_user",
    expected_kind="selector",
    break_selector='[data-test="add-to-cart-sauce-labs-backpack"]',
)


def load_cases() -> list[Case]:
    """Full coverage: every discovered journey as a baseline, plus the break/heal cases."""
    from agents.discovery import load_catalog
    from credentials import DEFAULT_USER

    # 1. Baseline: run every discovered journey as the working user (each should pass).
    cases = [
        Case(id=f"{flow.id}__baseline", user=DEFAULT_USER, expected_kind=None, flow_id=flow.id)
        for flow in load_catalog()
    ]

    # 2. Break-user matrix on checkout (the negative cases). Skip the control user —
    #    the checkout baseline already covers it.
    if BREAK_MATRIX_YAML.exists():
        data = yaml.safe_load(BREAK_MATRIX_YAML.read_text(encoding="utf-8"))
        for user, info in data.items():
            if user == DEFAULT_USER:
                continue
            cases.append(Case(
                id=f"checkout_{user}", user=user, expected_kind=info.get("observed_kind"),
            ))

    # 3. The genuine, healable selector-break case.
    cases.append(SELECTOR_BREAK_CASE)
    return cases


if __name__ == "__main__":
    for c in load_cases():
        print(f"{c.id:34s} user={c.user:26s} expected={c.expected_kind or 'pass'}")
