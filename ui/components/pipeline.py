"""Pipeline View Component (G1) — Renders the agent state flow visually."""
from __future__ import annotations

import streamlit as st
from schemas import AgentState


def render_pipeline(state: AgentState) -> None:
    """Render a visual, glassmorphic pipeline representation of the self-healing loop."""
    # Determine the status class for each stage.
    # Statuses can be: "pending", "active", "pass", "fail"

    # 1. Discovery
    if state.flow is not None:
        disc_status = "pass"
    else:
        disc_status = "active"

    # 2. Script Gen
    if state.script is not None:
        gen_status = "pass"
    elif disc_status == "pass":
        gen_status = "active"
    else:
        gen_status = "pending"

    # 3. Execution
    exec_status = "pending"
    if state.result is not None:
        if state.result.status == "pass":
            exec_status = "pass"
        elif state.result.status == "fail":
            exec_status = "fail"
    elif gen_status == "pass":
        exec_status = "active"

    # 4. Diagnosis
    diag_status = "pending"
    if state.diagnosis is not None:
        diag_status = "pass"
    elif exec_status == "fail":
        diag_status = "active"

    # 5. Repair
    repair_status = "pending"
    attempts_badge = ""
    if len(state.repair_attempts) > 0:
        last_attempt = state.repair_attempts[-1]
        attempts_badge = f"<span class='status-badge pass' style='margin-top: 5px;'>Attempt {last_attempt.attempt_no}</span>"
        if last_attempt.result is not None:
            if last_attempt.result.status == "pass":
                repair_status = "pass"
            else:
                repair_status = "fail"
        else:
            repair_status = "active"
    elif diag_status == "pass":
        repair_status = "active"

    # Helper function to get emoji and label classes
    def get_node_html(label: str, status: str, icon: str, extra: str = "") -> str:
        active_class = "active" if status == "active" else ""
        pass_class = "pass" if status == "pass" else ""
        fail_class = "fail" if status == "fail" else ""
        pending_class = "pending" if status == "pending" else ""

        status_class = active_class or pass_class or fail_class or pending_class

        return f"""
        <div class="pipeline-node {status_class}">
            <div style="font-size: 1.8rem; margin-bottom: 5px;">{icon}</div>
            <div style="font-weight: 600; font-size: 0.9rem;">{label}</div>
            <div style="font-size: 0.75rem; text-transform: uppercase; margin-top: 4px; opacity: 0.8;" class="{status_class}">
                {status}
            </div>
            {extra}
        </div>
        """

    # Generate visual layout
    html = f"""
    <div class="pipeline-container">
        {get_node_html("Discovery", disc_status, "🔍")}
        <div class="pipeline-connector {'active' if gen_status != 'pending' else ''}"></div>
        {get_node_html("Script Gen", gen_status, "📝")}
        <div class="pipeline-connector {'active' if exec_status != 'pending' else ''}"></div>
        {get_node_html("Execution", exec_status, "🚀")}
        <div class="pipeline-connector {'active' if diag_status != 'pending' else ''}"></div>
        {get_node_html("Diagnosis", diag_status, "🩺")}
        <div class="pipeline-connector {'active' if repair_status != 'pending' else ''}"></div>
        {get_node_html("Repair", repair_status, "🔧", attempts_badge)}
    </div>
    """

    st.html(html)
