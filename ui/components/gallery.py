"""Artifact Gallery Component (G2) — Renders screenshots, video, logs, and diagnoses."""
from __future__ import annotations

import os

import streamlit as st

from schemas import AgentState


def render_heal_summary(state: AgentState) -> None:
    """Narrate what broke, how it was diagnosed, and how it healed — the demo story."""
    broke = state.result is not None and state.result.status == "fail"
    if not state.repair_attempts and not broke:
        return  # happy path — nothing to narrate

    st.subheader("🔁 Self-Healing Summary")
    with st.container(border=True):
        col_broke, col_diag, col_heal = st.columns(3)
        with col_broke:
            st.markdown("**❌ What broke**")
            corrupted = next(
                (s.selector for s in (state.flow.steps if state.flow else [])
                 if "-BROKEN" in s.selector),
                None,
            )
            if corrupted:
                st.markdown(f"Corrupted selector:\n\n`{corrupted}`")
            err = state.result.error if state.result else None
            if err:
                st.markdown(f"Error: `{err.kind}` at step {err.step_index}")
        with col_diag:
            st.markdown("**🩺 Diagnosis**")
            if state.diagnosis:
                st.markdown(state.diagnosis.root_cause)
                st.caption(f"confidence {state.diagnosis.confidence * 100:.0f}%")
            else:
                st.markdown("_pending_")
        with col_heal:
            st.markdown("**✅ How it healed**")
            healed = (
                state.result is not None
                and state.result.status == "pass"
                and len(state.repair_attempts) > 0
            )
            if healed:
                st.markdown(
                    "Rewrote the script and re-ran → **passed** "
                    f"after {len(state.repair_attempts)} attempt(s)."
                )
            elif state.repair_attempts:
                st.markdown(
                    f"Attempted {len(state.repair_attempts)} repair(s) — "
                    "not verified as a genuine heal."
                )
            else:
                st.markdown("_no repair yet_")

    # Before / after scripts, side by side (the broken script is the flow re-rendered).
    if state.repair_attempts and state.flow and state.script:
        from agents.script_gen import render_script

        st.markdown("**Script: before (broken) → after (AI-repaired)**")
        before_col, after_col = st.columns(2)
        with before_col:
            st.caption("Before — the generated script that failed")
            st.code(render_script(state.flow), language="python")
        with after_col:
            st.caption("After — the repaired script that passed")
            st.code(state.script.code, language="python")


def render_gallery(state: AgentState) -> None:
    """Render the error diagnosis details, before/after code diff, screenshots, and logs."""
    render_heal_summary(state)
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
                            # Fallback when the file isn't on disk (e.g. mock states) —
                            # a self-contained placeholder, no external network call.
                            st.html(
                                '<div class="artifact-card">'
                                '<div class="artifact-icon">🖼️</div>'
                                f'<div class="artifact-name">{os.path.basename(img_path)}</div>'
                                "</div>"
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
