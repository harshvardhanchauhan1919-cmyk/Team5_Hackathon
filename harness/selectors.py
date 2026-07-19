"""C1 — Swag Labs checkout flow baseline: the frozen data-test selector set
that Script Generator generates against, and that Diagnosis / the break-matrix
diff against.

Run:  python -m harness.selectors
Walks the flow live as standard_user, verifies every selector below actually
resolves, and (re)writes harness/selectors.md as the human-readable baseline doc.
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from credentials import DEFAULT_USER, PASSWORD
from harness.step_executor import run_flow
from schemas import Flow, Step

TARGET_URL = "https://www.saucedemo.com/"

CHECKOUT_FLOW = Flow(
    id="checkout",
    name="Login -> add backpack -> checkout -> finish",
    target_url=TARGET_URL,
    steps=[
        Step(action="goto", value=TARGET_URL, description="Open Swag Labs login page"),
        Step(action="fill", selector='[data-test="username"]', value="{username}",
             description="Enter username"),
        Step(action="fill", selector='[data-test="password"]', value="{password}",
             description="Enter password"),
        Step(action="click", selector='[data-test="login-button"]', description="Submit login"),
        Step(action="assert_visible", selector='[data-test="inventory-container"]',
             description="Land on inventory page"),
        Step(action="click", selector='[data-test="add-to-cart-sauce-labs-backpack"]',
             description="Add Sauce Labs Backpack to cart"),
        Step(action="assert_text", selector='[data-test="shopping-cart-badge"]', value="1",
             description="Cart badge increments to 1"),
        Step(action="click", selector='[data-test="shopping-cart-link"]', description="Open cart"),
        Step(action="assert_visible", selector='[data-test="checkout"]',
             description="Cart page shows checkout button"),
        Step(action="click", selector='[data-test="checkout"]', description="Begin checkout"),
        Step(action="fill", selector='[data-test="firstName"]', value="Test",
             description="Enter first name"),
        Step(action="fill", selector='[data-test="lastName"]', value="User",
             description="Enter last name"),
        Step(action="fill", selector='[data-test="postalCode"]', value="12345",
             description="Enter postal code"),
        Step(action="click", selector='[data-test="continue"]', description="Continue to overview"),
        Step(action="assert_visible", selector='[data-test="finish"]',
             description="Overview page shows finish button"),
        Step(action="click", selector='[data-test="finish"]', description="Finish checkout"),
        Step(action="assert_visible", selector='[data-test="complete-header"]',
             description="Order complete confirmation shown"),
    ],
)

DOC_PATH = Path(__file__).parent / "selectors.md"


def capture_and_verify(headless: bool = True) -> list[dict]:
    """Walk CHECKOUT_FLOW live as standard_user; confirm every selector resolves."""
    report: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        context = {"username": DEFAULT_USER, "password": PASSWORD}
        outcome = run_flow(page, CHECKOUT_FLOW.steps, context)
        for s in outcome.steps:
            report.append({
                "step_index": s.step_index,
                "action": s.step.action,
                "selector": s.step.selector,
                "description": s.step.description,
                "ok": s.ok,
                "duration_s": round(s.duration_s, 3),
                "note": s.note,
            })
        browser.close()
    if outcome.error is not None:
        raise RuntimeError(
            f"C1 baseline walk failed at step {outcome.error.step_index} "
            f"({outcome.error.kind}): {outcome.error.message} — fix the baseline first."
        )
    return report


def write_baseline_doc(report: list[dict], path: Path = DOC_PATH) -> None:
    lines = [
        "# Swag Labs checkout flow — selector baseline (C1)",
        "",
        "Verified live against https://www.saucedemo.com/ as `standard_user`.",
        "This is the ground truth Script Generator generates against and Diagnosis diffs against.",
        "",
        "| # | Action | Selector | Description | Verified | Duration (s) |",
        "|---|---|---|---|---|---|",
    ]
    for r in report:
        selector = f"`{r['selector']}`" if r["selector"] else "—"
        lines.append(
            f"| {r['step_index']} | {r['action']} | {selector} | {r['description']} | "
            f"{'OK' if r['ok'] else 'FAIL'} | {r['duration_s']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    report = capture_and_verify()
    write_baseline_doc(report)
    print(f"C1 baseline verified: {len(report)} steps OK -> {DOC_PATH}")
