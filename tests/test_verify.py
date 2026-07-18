"""Unit tests for the verification hook (F3)."""
from __future__ import annotations

from harness.verify import verify_healed
from schemas import Error, RunResult


def test_verify_healed_success():
    result = RunResult(script_id="test", status="pass")
    assert verify_healed(result) is True


def test_verify_healed_failed_status():
    result = RunResult(script_id="test", status="fail")
    assert verify_healed(result) is False


def test_verify_healed_with_error():
    result = RunResult(
        script_id="test",
        status="pass",
        error=Error(kind="selector", message="hidden error", step_index=2),
    )
    assert verify_healed(result) is False


def test_verify_healed_with_original_context():
    original = RunResult(
        script_id="test",
        status="fail",
        error=Error(kind="selector", message="selector failed", step_index=3),
    )
    result = RunResult(script_id="test", status="pass")
    assert verify_healed(result, original_result=original) is True
