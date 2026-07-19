"""Artifact Gallery Component (G2) — Renders screenshots, video, logs, and diagnoses."""
from __future__ import annotations

import os

import streamlit as st

from schemas import AgentState


def render_gallery(state: AgentState) -> None:
    """Render the error diagnosis details, before/after code diff, screenshots, and logs."""
    st.subheader("🖼️ Artifact Gallery & Run Details")

    # 1. Error & Diagnosis Section (if failure occurred)
    if state.result and state.result.status == "fail":
        with st.container(border=True):
            st.markdown(
                "<h4 style='color:#ef4444; margin-top:0;'>❌ Execution Failure Detected</h4>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"**Error Kind:** `{state.result.error.kind if state.result.error else 'N/A'}`"
                )
                error_message = state.result.error.message if state.result.error else "N/A"
                step_index = state.result.error.step_index if state.result.error else "N/A"
                st.markdown(f"**Error Message:** `{error_message}`")
                st.markdown(f"**Step Index:** `{step_index}`")

            with col2:
                if state.diagnosis:
                    st.markdown(
                        "<h5 style='color:#3b82f6; margin-top:0;'>🩺 Diagnosis Report</h5>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Root Cause:** {state.diagnosis.root_cause}")
                    st.markdown(f"**Confidence:** `{state.diagnosis.confidence * 100:.1f}%`")
                    st.markdown(f"**Suggested Fix:** *{state.diagnosis.suggested_fix}*")
                else:
                    st.warning("Diagnosis pending...")

    # 2. Before / After Scripts Comparison
    with st.container(border=True):
        st.markdown("<h4 style='margin-top:0;'>📝 Script Code View</h4>", unsafe_allow_html=True)

        script_tab1, script_tab2 = st.tabs(["Original / Current Script", "Repaired Script History"])

        with script_tab1:
            if state.script:
                st.code(state.script.code, language="python")
            else:
                st.info("No script generated yet.")

        with script_tab2:
            if state.repair_attempts:
                for idx, attempt in enumerate(state.repair_attempts):
                    st.markdown(f"##### Repair Attempt #{attempt.attempt_no}")
                    st.code(attempt.new_script.code, language="python")
                    if attempt.result:
                        st.write(f"Result Status: **{attempt.result.status.upper()}**")
                    st.divider()
            else:
                st.info("No repair attempts made yet.")

    # 3. Screenshots and Logs
    with st.container(border=True):
        st.markdown("<h4 style='margin-top:0;'>📷 Screenshots & Logs</h4>", unsafe_allow_html=True)

        media_tab1, media_tab2 = st.tabs(["Screenshots", "Execution Logs"])

        with media_tab1:
            # Collect all screenshots from original run and repair attempts
            all_screenshots = []
            if state.result and state.result.screenshots:
                for s in state.result.screenshots:
                    all_screenshots.append((s, "Original Run"))

            for attempt in state.repair_attempts:
                if attempt.result and attempt.result.screenshots:
                    for s in attempt.result.screenshots:
                        all_screenshots.append((s, f"Repair Attempt #{attempt.attempt_no}"))

            if all_screenshots:
                cols = st.columns(min(len(all_screenshots), 3))
                for idx, (img_path, label) in enumerate(all_screenshots):
                    col_idx = idx % len(cols)
                    with cols[col_idx]:
                        st.write(f"**{label}**")
                        if os.path.exists(img_path):
                            # Real browser capture from the Execution node.
                            st.image(img_path, caption=img_path)
                        else:
                            # Fallback when the file isn't on disk (e.g. mock states).
                            st.image(
                                "https://placehold.co/600x400/0f172a/e2e8f0/png?text="
                                + os.path.basename(img_path).replace(" ", "+"),
                                caption=img_path,
                            )
            else:
                st.info("No screenshots available.")

        with media_tab2:
            if state.result:
                st.markdown("**Original Run Logs:**")
                st.code(state.result.logs)

            for attempt in state.repair_attempts:
                if attempt.result:
                    st.markdown(f"**Repair Attempt #{attempt.attempt_no} Logs:**")
                    st.code(attempt.result.logs)

            if not state.result and not state.repair_attempts:
                st.info("No logs available yet.")
