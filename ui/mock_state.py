"""Mock state for local UI testing and development (G1-G3).

Allows launching the UI and viewing the pipeline, agent runs, and healing process
without needing to execute the real LangGraph graph or live LLMs.
"""
from __future__ import annotations

from credentials import DEFAULT_USER, PASSWORD
from schemas import (
    AgentState,
    Diagnosis,
    Error,
    Flow,
    RepairAttempt,
    RunResult,
    Script,
    Step,
)

# Define mock steps representing a Swag Labs login -> checkout sequence.
MOCK_STEPS = [
    Step(
        action="goto",
        value="https://www.saucedemo.com/",
        description="Navigate to Swag Labs login page",
    ),
    Step(
        action="fill",
        selector="[data-test='username']",
        value=DEFAULT_USER,
        description="Fill in username",
    ),
    Step(
        action="fill",
        selector="[data-test='password']",
        value=PASSWORD,
        description="Fill in password",
    ),
    Step(
        action="click",
        selector="[data-test='login-button']",
        description="Click login button",
    ),
    Step(
        action="click",
        selector="[data-test='add-to-cart-sauce-labs-backpack']",
        description="Add backpack to cart",
    ),
    Step(
        action="click",
        selector="[data-test='shopping-cart-link']",
        description="Go to cart page",
    ),
    Step(
        action="click",
        selector="[data-test='checkout-btn-renamed']",
        description="Click checkout button",
    ),
]

MOCK_FLOW = Flow(
    id="swag_labs_checkout",
    name="Swag Labs Checkout Flow",
    steps=MOCK_STEPS,
    target_url="https://www.saucedemo.com/",
)

MOCK_INITIAL_SCRIPT = Script(
    flow_id="swag_labs_checkout",
    code="""\
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com/")
        page.fill("[data-test='username']", DEFAULT_USER)
        page.fill("[data-test='password']", PASSWORD)
        page.click("[data-test='login-button']")
        page.click("[data-test='add-to-cart-sauce-labs-backpack']")
        page.click("[data-test='shopping-cart-link']")
        page.click("[data-test='checkout-btn-renamed']") # FAILS HERE
        browser.close()

if __name__ == "__main__":
    run()
""",
)

MOCK_FAILED_RESULT = RunResult(
    script_id="swag_labs_checkout",
    status="fail",
    logs=(
        "Navigating to https://www.saucedemo.com/\n"
        "Filling username field\n"
        "Filling password field\n"
        "Clicking login button\n"
        "Adding backpack to cart\n"
        "Navigating to cart\n"
        "Waiting for locator(\"[data-test='checkout-btn-renamed']\")\n"
        "Error: locator.click: Timeout 5000ms exceeded.\n"
        "  at /path/to/script.py:10\n"
    ),
    screenshots=["screenshot_failure_step_7.png"],
    error=Error(
        kind="selector",
        message="Timeout 5000ms exceeded waiting for selector [data-test='checkout-btn-renamed']",
        step_index=6,
    ),
)

MOCK_DIAGNOSIS = Diagnosis(
    error=MOCK_FAILED_RESULT.error,
    root_cause=(
        "The checkout button selector '[data-test='checkout-btn-renamed']' did not match "
        "any element on the page. The button's actual data-test attribute value is "
        "'[data-test='checkout']'."
    ),
    confidence=0.95,
    suggested_fix="Replace '[data-test='checkout-btn-renamed']' with '[data-test='checkout']'.",
)

MOCK_REPAIRED_SCRIPT = Script(
    flow_id="swag_labs_checkout",
    code="""\
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com/")
        page.fill("[data-test='username']", DEFAULT_USER)
        page.fill("[data-test='password']", PASSWORD)
        page.click("[data-test='login-button']")
        page.click("[data-test='add-to-cart-sauce-labs-backpack']")
        page.click("[data-test='shopping-cart-link']")
        page.click("[data-test='checkout']") # HEALED: Updated selector
        browser.close()

if __name__ == "__main__":
    run()
""",
)

MOCK_PASSED_RESULT = RunResult(
    script_id="swag_labs_checkout",
    status="pass",
    logs=(
        "Navigating to https://www.saucedemo.com/\n"
        "Filling username field\n"
        "Filling password field\n"
        "Clicking login button\n"
        "Adding backpack to cart\n"
        "Navigating to cart\n"
        "Clicking checkout button\n"
        "Run completed successfully!\n"
    ),
    screenshots=["screenshot_checkout_step_one.png", "screenshot_success.png"],
)

# ---------------------------------------------------------------------------
# Pre-packaged AgentStates representing different stages of execution
# ---------------------------------------------------------------------------

# 1. State right after discovery and code generation (happy path starting)
state_pending = AgentState(
    flow=MOCK_FLOW,
    script=MOCK_INITIAL_SCRIPT,
    result=None,
    diagnosis=None,
    repair_attempts=[],
)

# 2. State when the first run fails
state_failed = AgentState(
    flow=MOCK_FLOW,
    script=MOCK_INITIAL_SCRIPT,
    result=MOCK_FAILED_RESULT,
    diagnosis=None,
    repair_attempts=[],
)

# 3. State when the diagnosis is made
state_diagnosed = AgentState(
    flow=MOCK_FLOW,
    script=MOCK_INITIAL_SCRIPT,
    result=MOCK_FAILED_RESULT,
    diagnosis=MOCK_DIAGNOSIS,
    repair_attempts=[],
)

# 4. State after the script is repaired and running successfully
state_healed = AgentState(
    flow=MOCK_FLOW,
    script=MOCK_REPAIRED_SCRIPT,
    result=MOCK_PASSED_RESULT,
    diagnosis=MOCK_DIAGNOSIS,
    repair_attempts=[
        RepairAttempt(
            diagnosis=MOCK_DIAGNOSIS,
            new_script=MOCK_REPAIRED_SCRIPT,
            attempt_no=1,
            result=MOCK_PASSED_RESULT,
        )
    ],
)
