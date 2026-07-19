"""Main entry point for the Streamlit UI dashboard (G1-G3)."""
from __future__ import annotations

import os
import sys

import streamlit as st

# Ensure repository root is in python path for Streamlit imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import AgentState
from ui.components.gallery import render_gallery
from ui.components.pipeline import render_pipeline
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
        st.sidebar.info("Runs the compiled LangGraph pipeline live against Swag Labs.")

        # Pick a scenario. "Break a selector" is the one that reliably heals — it's a
        # real script-vs-page break the AI can fix (see harness SELECTOR_BREAK_CASE).
        scenario = st.sidebar.selectbox(
            "Scenario",
            [
                "Healthy run (standard_user, should pass)",
                "Break a selector (should heal)",
                "problem_user (buggy account)",
                "performance_glitch_user (slow account)",
            ],
            index=1,
        )
        _CONFIGS = {
            "Healthy run (standard_user, should pass)": {"user": "standard_user"},
            "Break a selector (should heal)": {
                "user": "standard_user",
                "break_selector": '[data-test="add-to-cart-sauce-labs-backpack"]',
            },
            "problem_user (buggy account)": {"user": "problem_user"},
            "performance_glitch_user (slow account)": {"user": "performance_glitch_user"},
        }

        if st.sidebar.button("Run Live Pipeline"):
            from graph.build import build_graph

            st.sidebar.warning("Executing Graph...")
            try:
                app = build_graph()
                configurable = {
                    "flow_id": "e2e_checkout",
                    "target_url": "https://www.saucedemo.com/",
                    **_CONFIGS[scenario],
                }
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


if __name__ == "__main__":
    main()
