"""Case matrix for the local `test_website` target — a Vite/React clone of Swag Labs
that can be genuinely broken server-side via a `?break=<mode>` query param.

Why this exists alongside harness.cases: harness.cases's `SELECTOR_BREAK_CASE` only
gets a healable failure by client-side string-mangling a selector it already knows is
correct (`_corrupt_selector` in agents/discovery.py appends "-BROKEN" to a selector).
The LLM can trivially reverse that specific mutation — it isn't evidence the pipeline
can diagnose a *real* DOM change. test_website's break modes really rename the
data-test attribute in the rendered page (see test_website/README.md "Break Modes"),
so a case here is a genuine script-vs-page mismatch the healing loop has to solve
blind, same as it would against any real site update.

Start the site first:
    cd test_website && npm run dev   # serves http://localhost:3000

Run the matrix (pick a backend — see README.md "Run modes"):
    LLM_BACKEND=opencode python -m harness.test_website_runner
    LLM_BACKEND=claude   python -m harness.test_website_runner
    LLM_BACKEND=api      python -m harness.test_website_runner   # needs OPENROUTER_API_KEY
"""
from __future__ import annotations

from harness.cases import Case

BASE_URL = "http://localhost:3000/"
FLOW_ID = "e2e_checkout"
USER = "standard_user"

# mode -> (expected_kind for reporting, human note on the real DOM change it makes)
BREAK_MODES: dict[str, tuple[str | None, str]] = {
    "cart_selector": ("missing_element", 'data-test="shopping-cart-link" -> "cart-link-v2"'),
    "continue_selector": ("missing_element", 'data-test="continue" -> "continue-checkout"'),
    "complete_selector": (
        "missing_element",
        'data-test="complete-header" -> "order-complete-title"',
    ),
    "checkout_delay": (
        None,
        "3000ms navigation delay, information -> overview (may not fail at all "
        "under Playwright's default 30s auto-wait; kept as a control case)",
    ),
}


def load_test_website_cases() -> list[Case]:
    """Baseline (no break) + one case per documented break mode."""
    cases = [
        Case(
            id="test_website__baseline",
            user=USER,
            expected_kind=None,
            flow_id=FLOW_ID,
            target_url=BASE_URL,
        )
    ]
    for mode, (expected_kind, _note) in BREAK_MODES.items():
        cases.append(Case(
            id=f"test_website__{mode}",
            user=USER,
            expected_kind=expected_kind,
            flow_id=FLOW_ID,
            target_url=f"{BASE_URL}?break={mode}",
        ))
    return cases


if __name__ == "__main__":
    for c in load_test_website_cases():
        print(f"{c.id:34s} target={c.target_url}")
