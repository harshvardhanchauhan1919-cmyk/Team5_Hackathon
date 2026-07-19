"""Selector Baseline (C1) section — renders harness.selectors' live output on the dashboard.

Mirrors harness/selectors.md exactly (same title text, comment lines, and column layout)
so the webpage shows what that script verified without needing to open the generated file.
"""
from __future__ import annotations

import streamlit as st

from harness.selectors import CHECKOUT_FLOW, TARGET_URL, capture_and_verify
from ui.components.tables import badge, cell, mono_cell, render_table


def render_selector_baseline() -> None:
    """Button-triggered (it drives a real Playwright run against Swag Labs) section
    showing the C1 baseline table once harness.selectors.capture_and_verify() finishes."""
    with st.container(border=True):
        st.markdown(
            "<h4 style='margin-top:0;'>🧭 Selector Baseline (C1)</h4>", unsafe_allow_html=True
        )

        if st.button("Run Selector Baseline (C1)"):
            with st.spinner("Walking the checkout flow live against Swag Labs..."):
                try:
                    st.session_state["selector_baseline_report"] = capture_and_verify()
                except Exception as exc:  # noqa: BLE001
                    st.session_state["selector_baseline_error"] = str(exc)
                    st.session_state.pop("selector_baseline_report", None)
                else:
                    st.session_state.pop("selector_baseline_error", None)

        error = st.session_state.get("selector_baseline_error")
        if error:
            st.error(f"Selector baseline failed: {error}")

        report = st.session_state.get("selector_baseline_report")
        if not report:
            st.info("Run the selector baseline above to see the live C1 verification here.")
            return

        st.markdown(f"##### Selector baseline – {CHECKOUT_FLOW.name}")
        st.caption(
            f"Verified live against {TARGET_URL} as `standard_user`. This is the ground "
            "truth Script Generator generates against and Diagnosis diffs against."
        )

        headers = ["#", "Action", "Selector", "Description", "Verified", "Duration (s)"]
        rows = [
            [
                cell(r["step_index"]),
                cell(r["action"]),
                mono_cell(r["selector"]) if r["selector"] else "—",
                cell(r["description"]),
                badge("OK", "pass") if r["ok"] else badge("FAIL", "fail"),
                cell(r["duration_s"]),
            ]
            for r in report
        ]
        render_table(headers, rows)
