"""F3 (bonus) — Regression Monitor: visual diff of new screenshots against a
stored baseline, per PRD v2 §4. Explicitly a stretch goal — build/run this
only after C1-C3 and F1-F3's mandatory verify are solid; it is not required
for the demo.

Run:  python -m harness.regression_monitor
Seeds harness/fixtures/baseline_screenshots/ on first run per user, then
flags any later run whose screenshot drifts past `threshold` from that baseline.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops

BASELINE_DIR = Path(__file__).parent / "fixtures" / "baseline_screenshots"
DEFAULT_THRESHOLD = 0.05  # fraction of max pixel-diff; tune once real UI screenshots exist


@dataclass
class RegressionResult:
    baseline: Path
    candidate: Path
    diff_ratio: float  # 0.0 = identical, 1.0 = completely different
    regressed: bool


def diff_ratio(baseline_path: Path, candidate_path: Path) -> float:
    baseline = Image.open(baseline_path).convert("RGB")
    candidate = Image.open(candidate_path).convert("RGB").resize(baseline.size)
    diff = ImageChops.difference(baseline, candidate)
    hist = diff.convert("L").histogram()
    weighted = sum(count * value for value, count in enumerate(hist))
    max_possible = 255 * baseline.width * baseline.height
    return weighted / max_possible if max_possible else 0.0


def check_regression(
    user: str, candidate_path: Path, threshold: float = DEFAULT_THRESHOLD
) -> RegressionResult:
    baseline_path = BASELINE_DIR / f"{user}.png"
    if not baseline_path.exists():
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(candidate_path, baseline_path)
        return RegressionResult(baseline_path, candidate_path, 0.0, False)
    ratio = diff_ratio(baseline_path, candidate_path)
    return RegressionResult(baseline_path, candidate_path, ratio, ratio > threshold)


if __name__ == "__main__":
    from harness.break_matrix import EVIDENCE_DIR, USERS

    for user in USERS:
        shot = EVIDENCE_DIR / f"{user}.png"
        if not shot.exists():
            print(f"[regression] no evidence screenshot for {user}, skip "
                  "(run `python -m harness.break_matrix` first)")
            continue
        result = check_regression(user, shot)
        status = "REGRESSED" if result.regressed else "ok"
        print(f"[regression] {user}: diff={result.diff_ratio:.3f} -> {status}")
