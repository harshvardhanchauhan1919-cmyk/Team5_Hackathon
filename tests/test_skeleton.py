"""Smoke test for the walking skeleton — LLM mocked, no network."""
from graph.build import build_graph
from schemas import AgentState


def test_pipeline_runs_end_to_end():
    app = build_graph()
    final = app.invoke(AgentState())
    result = final.get("result") if isinstance(final, dict) else final.result
    assert result is not None
    assert result.status in {"pass", "fail"}
