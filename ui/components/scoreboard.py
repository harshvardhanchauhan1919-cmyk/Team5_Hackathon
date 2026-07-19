"""Scoreboard (F2) section for harness result files."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from harness.metrics import AUTO_REPAIR_TARGET, REPORT_JSON, summarize
from ui.components.tables import badge, cell, render_table

_CACHE_KEY_PREFIX = "scoreboard_cache"


def _load_results(report_json: Path) -> list[dict]:
    if not report_json.exists():
        raise FileNotFoundError(f"no {report_json} - run the matching harness first")
    return json.loads(report_json.read_text(encoding="utf-8"))


def render_scoreboard(
    title: str = "Scoreboard - auto-repair metrics",
    report_json: Path = REPORT_JSON,
) -> None:
    """Render F2 metrics for any harness report with the standard result schema."""
    cache_key = f"{_CACHE_KEY_PREFIX}:{report_json}"
    with st.container(border=True):
        st.markdown(
            f"<h4 style='margin-top:0;'>📊 {title}</h4>",
            unsafe_allow_html=True,
        )

        if st.button("Refresh Scoreboard (F2)", key=f"refresh:{report_json}"):
            st.session_state.pop(cache_key, None)

        if cache_key not in st.session_state:
            try:
                results = _load_results(report_json)
            except FileNotFoundError as exc:
                st.info(str(exc))
                return
            st.session_state[cache_key] = (results, summarize(results))

        results, summary = st.session_state[cache_key]

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
