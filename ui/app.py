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

    # Active state placeholder
    current_state = state_pending

    if mode == "Mock State Player (Demo)":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎬 State Player Controls")
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

        # Apply sidebar-configured options to the current state
        current_state.hitl = hitl
        current_state.max_attempts = max_attempts

    else:
        # Live Graph Execution
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚀 Live Runner Controls")

        target_site = st.sidebar.selectbox(
            "Target site",
            ["Swag Labs (saucedemo.com)", "test_website (local, http://localhost:3000)"],
            index=0,
        )

        if target_site == "Swag Labs (saucedemo.com)":
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
                "not synthetic string corruption. Make sure `npm run dev` is running on "
                "http://localhost:3000."
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
                "Baseline (no break) — should pass": "http://localhost:3000/",
                "Break cart selector — should heal": "http://localhost:3000/?break=cart_selector",
                "Break continue selector — should heal": "http://localhost:3000/?break=continue_selector",
                "Break complete selector — should heal": "http://localhost:3000/?break=complete_selector",
                "Checkout delay — passes without healing (control case)":
                    "http://localhost:3000/?break=checkout_delay",
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
    render_selector_baseline()

    st.divider()
    saucedemo_tab, test_site_tab = st.tabs(["Saucedemo scoreboard", "test_site scoreboard"])
    with saucedemo_tab:
        render_scoreboard("Saucedemo scoreboard - auto-repair metrics")
    with test_site_tab:
        render_scoreboard(
            "test_site scoreboard - auto-repair metrics",
            Path(__file__).resolve().parents[1] / "harness" / "report_test_website.json",
        )


if __name__ == "__main__":
    main()
