"""Scoreboard (F2) section — renders harness.metrics' output on the dashboard.

Mirrors harness/report.md exactly (same conclusion line and both tables) so the webpage
shows the latest auto-repair numbers without needing to open the generated file.
"""
from __future__ import annotations

import streamlit as st

from harness.metrics import AUTO_REPAIR_TARGET, load_results, summarize
from ui.components.tables import badge, cell, render_table

_CACHE_KEY = "scoreboard_cache"


def render_scoreboard() -> None:
    """Reads harness/report.json (written by harness.runner) and shows the same
    conclusion line + tables that harness.metrics writes to harness/report.md."""
    with st.container(border=True):
        st.markdown(
            "<h4 style='margin-top:0;'>📊 Scoreboard — auto-repair metrics</h4>",
            unsafe_allow_html=True,
        )

        if st.button("Refresh Scoreboard (F2)"):
            st.session_state.pop(_CACHE_KEY, None)

        if _CACHE_KEY not in st.session_state:
            try:
                results = load_results()
            except FileNotFoundError as exc:
                st.info(str(exc))
                return
            st.session_state[_CACHE_KEY] = (results, summarize(results))

        results, summary = st.session_state[_CACHE_KEY]

        suspect_note = (
            f", {summary['suspect']} more flagged suspect by F3" if summary["suspect"] else ""
        )
        target_badge = badge("MET", "pass") if summary["meets_target"] else badge("NOT MET", "fail")
        st.markdown(
            f"**Auto-repair rate: {summary['auto_repair_rate']:.0%}** "
            f"({summary['healed']}/{summary['initially_failed']} initially-failed cases healed"
            f"{suspect_note}) "
            f"— target >= {AUTO_REPAIR_TARGET:.0%} {target_badge}",
            unsafe_allow_html=True,
        )

        st.markdown("###### By failure class")
        by_kind_headers = ["Failure class", "Attempted", "Healed (verified)", "Rate"]
        by_kind_rows = []
        for kind, counts in sorted(summary["by_kind"].items()):
            rate = counts["healed"] / counts["attempted"] if counts["attempted"] else 0
            by_kind_rows.append(
                [cell(kind), cell(counts["attempted"]), cell(counts["healed"]), cell(f"{rate:.0%}")]
            )
        render_table(by_kind_headers, by_kind_rows)

        st.markdown("###### Per-case detail")
        per_case_headers = [
            "Case", "User", "Expected class", "Initial", "Final",
            "Repair attempts", "Healed", "Verified",
        ]
        per_case_rows = [
            [
                cell(r["case_id"]),
                cell(r["user"]),
                cell(r["expected_kind"] or "pass"),
                badge("pass", "pass") if r["initial_status"] == "pass" else badge("fail", "fail"),
                badge("pass", "pass") if r["final_status"] == "pass" else badge("fail", "fail"),
                cell(r["repair_attempt_count"]),
                badge("yes", "pass") if r["healed"] else badge("no", "neutral"),
                (
                    badge("true", "pass") if r["verified_healed"] is True
                    else badge("false", "fail") if r["verified_healed"] is False
                    else badge("—", "neutral")
                ),
            ]
            for r in results
        ]
        render_table(per_case_headers, per_case_rows)
