"""Unit tests for the Adaptive Repair agent (E2)."""
from __future__ import annotations

import os
from unittest.mock import patch

from agents.repair import repair_node
from schemas import AgentState, Diagnosis, Error, RepairAttempt, RunResult, Script


def test_repair_node_success():
    # Force mock mode
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        state = AgentState(
            script=Script(flow_id="test_flow", code="page.click('[data-test=\"submit-btn\"]')"),
            diagnosis=Diagnosis(
                error=Error(kind="selector", message="Failed step", step_index=1),
                root_cause="Selector renamed",
                confidence=0.9,
                suggested_fix="Use checkout",
            ),
        )

        next_state = repair_node(state)

        assert next_state.script is not None
        assert "saucedemo.com" in next_state.script.code  # verifies mock script contains Swag Labs checkout
        assert len(next_state.repair_attempts) == 1
        assert next_state.repair_attempts[0].attempt_no == 1
        assert next_state.repair_attempts[0].diagnosis == state.diagnosis


def test_repair_node_strips_code_fences():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        from tools.mock_llm import FakeModel

        with patch.object(FakeModel, "invoke") as mock_invoke:
            class MockMsg:
                content = "```python\n# clean code here\nprint('hello')\n```"

            mock_invoke.return_value = MockMsg()

            state = AgentState(
                script=Script(flow_id="test", code="old code"),
                diagnosis=Diagnosis(
                    error=Error(kind="timeout", message="Timeout", step_index=0),
                    root_cause="Timeout delay",
                    confidence=0.8,
                    suggested_fix="Wait more",
                ),
            )

            next_state = repair_node(state)
            assert next_state.script is not None
            assert next_state.script.code == "# clean code here\nprint('hello')"


def test_repair_node_exception_handling():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        from tools.mock_llm import FakeModel

        # Mock exception thrown on invoke
        with patch.object(FakeModel, "invoke", side_effect=ValueError("connection timed out")):
            state = AgentState(
                script=Script(flow_id="test", code="original code"),
                diagnosis=Diagnosis(
                    error=Error(kind="selector", message="Failed selector", step_index=2),
                    root_cause="Selector missing",
                    confidence=0.7,
                    suggested_fix="Repair",
                ),
            )

            next_state = repair_node(state)
            assert next_state.script is not None
            # Fallback code should retain original script code, appended with attempt comment
            assert "original code" in next_state.script.code
            assert "failed: connection timed out" in next_state.script.code
            assert len(next_state.repair_attempts) == 1
            assert next_state.repair_attempts[0].new_script.code == next_state.script.code


def test_repair_node_history_formatting():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        # Inject multiple historical repair attempts and verify it formats and runs without failure
        state = AgentState(
            script=Script(flow_id="test", code="page.click('[data-test=\"submit-btn\"]')"),
            diagnosis=Diagnosis(
                error=Error(kind="selector", message="Failed step", step_index=1),
                root_cause="Selector renamed",
                confidence=0.9,
                suggested_fix="Use checkout",
            ),
            repair_attempts=[
                RepairAttempt(
                    diagnosis=Diagnosis(
                        error=Error(kind="selector", message="Err", step_index=1),
                        root_cause="Root cause 1",
                        suggested_fix="Fix 1",
                    ),
                    new_script=Script(flow_id="test", code="print('attempt 1')"),
                    attempt_no=1,
                    result=RunResult(script_id="test", status="fail"),
                ),
                RepairAttempt(
                    diagnosis=Diagnosis(
                        error=Error(kind="selector", message="Err", step_index=1),
                        root_cause="Root cause 2",
                        suggested_fix="Fix 2",
                    ),
                    new_script=Script(flow_id="test", code="print('attempt 2')"),
                    attempt_no=2,
                    result=RunResult(script_id="test", status="fail"),
                ),
            ],
        )

        next_state = repair_node(state)
        assert len(next_state.repair_attempts) == 3  # third attempt added
        assert next_state.repair_attempts[2].attempt_no == 3
