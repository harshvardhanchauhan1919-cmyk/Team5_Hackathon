"""Main entry point for the Streamlit UI dashboard (G1-G3)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

# Ensure repository root is in python path for Streamlit imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import AgentState
from ui.components.gallery import render_gallery
from ui.components.pipeline import render_pipeline
from ui.components.scoreboard import render_scoreboard
from ui.components.selector_baseline import render_selector_baseline
from ui.mock_state import state_diagnosed, state_failed, state_healed, state_pending

TARGET_SITE_OPTIONS = ["Swag Labs (saucedemo.com)", "test_website (local, http://localhost:3000)"]
DEFAULT_TEST_WEBSITE_URL = "http://localhost:3001/"
TEST_WEBSITE_REPORT = Path(__file__).resolve().parents[1] / "harness" / "report_test_website.json"

# Set page config for premium appearance
st.set_page_config(
    page_title="Self-Healing Playwright Agent Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    """Read theme.css and inject it into the app."""
    css_path = os.path.join(os.path.dirname(__file__), "components", "theme.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.html(f"<style>{css}</style>")


def normalize_base_url(url: str) -> str:
    url = url.strip()
    if not url:
        return DEFAULT_TEST_WEBSITE_URL
    return url if url.endswith("/") else f"{url}/"


def mock_state_for_target(state: AgentState, target_site: str, test_website_url: str) -> AgentState:
    """Return a demo state adjusted to the selected target site."""
    demo_state = state.model_copy(deep=True)
    if target_site == TARGET_SITE_OPTIONS[0]:
        return demo_state

    test_website_url = normalize_base_url(test_website_url)
    if demo_state.flow:
        steps = [
            step.model_copy(update={"value": test_website_url})
            if step.action == "goto"
            else step
            for step in demo_state.flow.steps
        ]
        demo_state.flow = demo_state.flow.model_copy(
            update={
                "id": "test_website_checkout",
                "name": "test_website Checkout Flow",
                "target_url": test_website_url,
                "steps": steps,
            }
        )

    scripts = [demo_state.script]
    scripts.extend(attempt.new_script for attempt in demo_state.repair_attempts)
    for script in scripts:
        if script:
            script.flow_id = "test_website_checkout"
            script.code = script.code.replace("https://www.saucedemo.com/", test_website_url)

    for result in [demo_state.result, demo_state.original_result]:
        if result:
            result.script_id = "test_website_checkout"
            result.logs = result.logs.replace("https://www.saucedemo.com/", test_website_url)

    return demo_state


def main() -> None:
    load_css()

    st.html(
        """
        <div style="display: flex; align-items: center; margin-bottom: 25px;">
            <span style="font-size: 2.5rem; margin-right: 15px;">🧠</span>
            <div>
                <h1 style="margin: 0; color: #e2e8f0; font-weight: 700; letter-spacing: -0.5px;">
                    Self-Healing Browser Automation
                </h1>
                <p style="margin: 0; color: #64748b; font-size: 1rem;">
                    LangGraph Healing Loop (feat/healing_loop) · AI-assisted
                    script diagnostics & repair
                </p>
            </div>
        </div>
        """
    )

    # ------------------------------------------------------------------
    # Sidebar config and controls
    # ------------------------------------------------------------------
    st.sidebar.title("🛠️ Controller & Config")

    mode = st.sidebar.selectbox(
        "Operation Mode",
        ["Mock State Player (Demo)", "Live Graph Execution"],
        index=0,
    )

    hitl = st.sidebar.checkbox("Enable Human-in-the-Loop Gate (HITL)", value=False)
    max_attempts = st.sidebar.number_input(
        "Max Healing Attempts",
        min_value=1,
        max_value=5,
        value=3,
    )
    target_site = st.sidebar.selectbox("Target site", TARGET_SITE_OPTIONS, index=0)
    test_website_url = DEFAULT_TEST_WEBSITE_URL
    if target_site == TARGET_SITE_OPTIONS[1]:
        test_website_url = normalize_base_url(
            st.sidebar.text_input("test_website URL", value=DEFAULT_TEST_WEBSITE_URL)
        )

    # Active state placeholder
    current_state = state_pending

    if mode == "Mock State Player (Demo)":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎬 State Player Controls")
        if target_site == TARGET_SITE_OPTIONS[0]:
            st.sidebar.info("Plays canned demo states against the Swag Labs target.")
        else:
            st.sidebar.info(f"Plays canned demo states against `{test_website_url}`.")

        playback_step = st.sidebar.radio(
            "Select Execution Stage:",
            [
                "1. Initial Discovery (Pending)",
                "2. First Run Failed (Error Detected)",
                "3. Error Diagnosed (Root Cause Found)",
                "4. Script Healed (Re-run Passed)",
            ],
            index=0,
        )

        # Load correct mock state
        if "1." in playback_step:
            current_state = state_pending
        elif "2." in playback_step:
            current_state = state_failed
        elif "3." in playback_step:
            current_state = state_diagnosed
        elif "4." in playback_step:
            current_state = state_healed

        current_state = mock_state_for_target(current_state, target_site, test_website_url)

        # Apply sidebar-configured options to the current state
        current_state.hitl = hitl
        current_state.max_attempts = max_attempts

    else:
        # Live Graph Execution
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚀 Live Runner Controls")

        if target_site == TARGET_SITE_OPTIONS[0]:
            st.sidebar.info("Runs the compiled LangGraph pipeline live against Swag Labs.")

            # Scenarios. The two "break selector" runs are genuine script-vs-page breaks the
            # AI fixes (real heals). The locked-out account is an honest non-heal that F3
            # correctly rejects — a good contrast to show the verification actually works.
            scenario = st.sidebar.selectbox(
                "Scenario",
                [
                    "Healthy run (standard_user) — should pass",
                    "Break add-to-cart selector — should heal",
                    "Break checkout selector — should heal",
                    "Locked-out account — correctly NOT healed",
                ],
                index=1,
            )
            _CONFIGS = {
                "Healthy run (standard_user) — should pass": {"user": "standard_user"},
                "Break add-to-cart selector — should heal": {
                    "user": "standard_user",
                    "break_selector": '[data-test="add-to-cart-sauce-labs-backpack"]',
                },
                "Break checkout selector — should heal": {
                    "user": "standard_user",
                    "break_selector": '[data-test="checkout"]',
                },
                "Locked-out account — correctly NOT healed": {"user": "locked_out_user"},
            }
            base_configurable = {
                "flow_id": "e2e_checkout",
                "target_url": "https://www.saucedemo.com/",
                **_CONFIGS[scenario],
            }
        else:
            st.sidebar.info(
                "Runs the compiled LangGraph pipeline live against the local test_website "
                "clone — genuine server-side data-test attribute renames via ?break=<mode>, "
                f"not synthetic string corruption. Make sure it is running at `{test_website_url}`."
            )

            # Mirrors harness/test_website_cases.py's BREAK_MODES. All test_website cases
            # use standard_user and need no break_selector — the break is server-side and
            # already encoded in the target URL.
            scenario = st.sidebar.selectbox(
                "Scenario",
                [
                    "Baseline (no break) — should pass",
                    "Break cart selector — should heal",
                    "Break continue selector — should heal",
                    "Break complete selector — should heal",
                    "Checkout delay — passes without healing (control case)",
                ],
                index=1,
            )
            _TEST_WEBSITE_TARGETS = {
                "Baseline (no break) — should pass": test_website_url,
                "Break cart selector — should heal": f"{test_website_url}?break=cart_selector",
                "Break continue selector — should heal": (
                    f"{test_website_url}?break=continue_selector"
                ),
                "Break complete selector — should heal": (
                    f"{test_website_url}?break=complete_selector"
                ),
                "Checkout delay — passes without healing (control case)":
                    f"{test_website_url}?break=checkout_delay",
            }
            base_configurable = {
                "flow_id": "e2e_checkout",
                "target_url": _TEST_WEBSITE_TARGETS[scenario],
                "user": "standard_user",
            }

        if st.sidebar.button("Run Live Pipeline"):
            from graph.build import build_graph

            st.sidebar.warning("Executing Graph...")
            try:
                app = build_graph()
                configurable = base_configurable
                # Discovery reads flow/user/break from config; no need to pre-seed state.
                final_state_dict = app.invoke(
                    AgentState(max_attempts=max_attempts, hitl=hitl),
                    config={"configurable": configurable},
                )
                if isinstance(final_state_dict, dict):
                    current_state = AgentState(**final_state_dict)
                else:
                    current_state = final_state_dict

                st.sidebar.success("Graph execution complete!")
            except Exception as exc:
                st.sidebar.error(f"Live run failed: {exc}")

    # ------------------------------------------------------------------
    # Render main UI elements
    # ------------------------------------------------------------------

    # Render visual pipeline view (G1)
    render_pipeline(current_state)

    # Render gallery & log viewer (G2-G3)
    render_gallery(current_state)

    # ------------------------------------------------------------------
    # Harness output, surfaced on the same page (plan_ui_extension.md)
    # ------------------------------------------------------------------
    st.divider()
    if target_site == TARGET_SITE_OPTIONS[0]:
        render_selector_baseline()
    else:
        with st.container(border=True):
            st.markdown(
                "<h4 style='margin-top:0;'>🧭 Selector Baseline (C1)</h4>",
                unsafe_allow_html=True,
            )
            st.info("Selector baseline capture is only wired for the Saucedemo target.")

    st.divider()
    if target_site == TARGET_SITE_OPTIONS[0]:
        render_scoreboard("Saucedemo scoreboard - auto-repair metrics")
    else:
        render_scoreboard(
            "test_site scoreboard - auto-repair metrics",
            TEST_WEBSITE_REPORT,
        )


if __name__ == "__main__":
    main()
