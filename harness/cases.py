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

    def config(self) -> dict:
        """The RunnableConfig to pass to app.invoke() — how discovery_node picks the case."""
        return {
            "configurable": {
                "flow_id": self.flow_id,
                "user": self.user,
                "target_url": self.target_url,
            }
        }


def load_cases() -> list[Case]:
    if not BREAK_MATRIX_YAML.exists():
        raise FileNotFoundError(
            f"no {BREAK_MATRIX_YAML} — run `python -m harness.break_matrix` first (C2)"
        )
    data = yaml.safe_load(BREAK_MATRIX_YAML.read_text(encoding="utf-8"))
    return [
        Case(id=f"checkout_{user}", user=user, expected_kind=info.get("observed_kind"))
        for user, info in data.items()
    ]


if __name__ == "__main__":
    for c in load_cases():
        print(f"{c.id:34s} user={c.user:26s} expected={c.expected_kind or 'pass'}")
