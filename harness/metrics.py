"""F2 — the metrics table: auto-repair rate + which failure classes healed.
This is the scoreboard that goes in the video and README.

Run:  python -m harness.metrics   (reads harness/report.json, writes report.md)
"""
from __future__ import annotations

import json
from pathlib import Path

REPORT_JSON = Path(__file__).parent / "report.json"
REPORT_MD = Path(__file__).parent / "report.md"

AUTO_REPAIR_TARGET = 0.5


def load_results() -> list[dict]:
    if not REPORT_JSON.exists():
        raise FileNotFoundError(f"no {REPORT_JSON} — run `python -m harness.runner` first")
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def summarize(results: list[dict]) -> dict:
    initially_failed = [r for r in results if r["initial_status"] == "fail"]
    # Only a *verified* heal counts toward the headline rate (F3) — a "healed"
    # flag the independent re-run couldn't confirm is a suspect, not a win.
    healed = [r for r in initially_failed if r["healed"] and r["verified_healed"]]
    suspect = [r for r in initially_failed if r["healed"] and not r["verified_healed"]]

    by_kind: dict[str, dict[str, int]] = {}
    for r in initially_failed:
        kind = r["expected_kind"] or r["final_error_kind"] or "unknown"
        by_kind.setdefault(kind, {"attempted": 0, "healed": 0})
        by_kind[kind]["attempted"] += 1
        if r in healed:
            by_kind[kind]["healed"] += 1

    rate = (len(healed) / len(initially_failed)) if initially_failed else 0.0
    return {
        "total_cases": len(results),
        "initially_failed": len(initially_failed),
        "healed": len(healed),
        "suspect": len(suspect),
        "auto_repair_rate": rate,
        "meets_target": rate >= AUTO_REPAIR_TARGET,
        "by_kind": by_kind,
    }


def render_markdown(results: list[dict], summary: dict) -> str:
    suspect_note = (
        f", {summary['suspect']} more flagged suspect by F3" if summary["suspect"] else ""
    )
    lines = [
        "# Scoreboard — auto-repair metrics (F2)",
        "",
        f"**Auto-repair rate: {summary['auto_repair_rate']:.0%}** "
        f"({summary['healed']}/{summary['initially_failed']} initially-failed cases healed"
        f"{suspect_note}) "
        f"— target >= {AUTO_REPAIR_TARGET:.0%} "
        f"{'MET' if summary['meets_target'] else 'NOT MET'}",
        "",
        "## By failure class",
        "",
        "| Failure class | Attempted | Healed (verified) | Rate |",
        "|---|---|---|---|",
    ]
    for kind, counts in sorted(summary["by_kind"].items()):
        rate = counts["healed"] / counts["attempted"] if counts["attempted"] else 0
        lines.append(f"| {kind} | {counts['attempted']} | {counts['healed']} | {rate:.0%} |")

    lines += [
        "",
        "## Per-case detail",
        "",
        "| Case | User | Expected class | Initial | Final | Repair attempts | "
        "Healed | Verified |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['case_id']} | {r['user']} | {r['expected_kind'] or 'pass'} | "
            f"{r['initial_status']} | {r['final_status']} | {r['repair_attempt_count']} | "
            f"{'yes' if r['healed'] else 'no'} | {r['verified_healed']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    results = load_results()
    summary = summarize(results)
    REPORT_MD.write_text(render_markdown(results, summary), encoding="utf-8")
    print(
        f"auto-repair rate: {summary['auto_repair_rate']:.0%} "
        f"({summary['healed']}/{summary['initially_failed']}, "
        f"{summary['suspect']} suspect) -> "
        f"{'MEETS' if summary['meets_target'] else 'BELOW'} the {AUTO_REPAIR_TARGET:.0%} target"
    )
    print(f"wrote {REPORT_MD}")
