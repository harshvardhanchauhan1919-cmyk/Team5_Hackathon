"""Unit tests for the Error Diagnosis agent (E1)."""
from __future__ import annotations

import os
from unittest.mock import patch

from agents.diagnosis import diagnosis_node
from schemas import AgentState, Error, RunResult


def test_diagnosis_node_success():
    # Force mock mode
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        state = AgentState(
            result=RunResult(
                script_id="test_flow",
                status="fail",
                logs="waiting for locator('[data-test=\"submit\"]')\nError: timeout",
                error=Error(
                    kind="selector",
                    message="Timeout waiting for selector",
                    step_index=2,
                ),
            )
        )

        next_state = diagnosis_node(state)

        assert next_state.diagnosis is not None
        assert "selector" in next_state.diagnosis.root_cause.lower()
        assert next_state.diagnosis.confidence == 0.92
        assert "data-test" in next_state.diagnosis.suggested_fix


def test_diagnosis_node_fallback_on_invalid_json():
    # Force mock mode and patch FakeModel.invoke to return invalid JSON
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        from tools.mock_llm import FakeModel

        with patch.object(FakeModel, "invoke") as mock_invoke:
            class MockMsg:
                content = "not a valid json string"

            mock_invoke.return_value = MockMsg()

            state = AgentState(
                result=RunResult(
                    script_id="test_flow",
                    status="fail",
                    error=Error(
                        kind="timeout",
                        message="Timeout error",
                        step_index=1,
                    ),
                )
            )

            next_state = diagnosis_node(state)

            # Verification should fallback gracefully and not throw exceptions
            assert next_state.diagnosis is not None
            assert next_state.diagnosis.confidence == 0.0
            assert "could not parse" in next_state.diagnosis.root_cause.lower()


def test_diagnosis_node_strips_markdown_fences():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        from tools.mock_llm import FakeModel

        with patch.object(FakeModel, "invoke") as mock_invoke:
            class MockMsg:
                content = (
                    "```json\n"
                    "{\n"
                    '  "root_cause": "markdown fenced root cause",\n'
                    '  "confidence": 0.85,\n'
                    '  "suggested_fix": "markdown fix"\n'
                    "}\n"
                    "```"
                )

            mock_invoke.return_value = MockMsg()

            state = AgentState(
                result=RunResult(
                    script_id="test_flow",
                    status="fail",
                    error=Error(
                        kind="selector",
                        message="some error",
                        step_index=3,
                    ),
                )
            )

            next_state = diagnosis_node(state)

            assert next_state.diagnosis is not None
            assert next_state.diagnosis.root_cause == "markdown fenced root cause"
            assert next_state.diagnosis.confidence == 0.85
            assert next_state.diagnosis.suggested_fix == "markdown fix"


def test_diagnosis_node_all_error_kinds():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        for kind in ("selector", "timeout", "missing_element", "flow_change"):
            state = AgentState(
                result=RunResult(
                    script_id="test_flow",
                    status="fail",
                    error=Error(
                        kind=kind,
                        message=f"{kind} message",
                        step_index=0,
                    ),
                )
            )

            next_state = diagnosis_node(state)
            assert next_state.diagnosis is not None
            assert next_state.diagnosis.error.kind == kind


def test_diagnosis_node_missing_logs_and_screenshots():
    with patch.dict(os.environ, {"USE_MOCK": "1"}):
        state = AgentState(
            result=RunResult(
                script_id="test_flow",
                status="fail",
                logs="",
                screenshots=[],
                error=Error(
                    kind="timeout",
                    message="Timeout waiting for locator",
                    step_index=1,
                ),
            )
        )

        next_state = diagnosis_node(state)
        assert next_state.diagnosis is not None
        assert next_state.diagnosis.confidence > 0.0
