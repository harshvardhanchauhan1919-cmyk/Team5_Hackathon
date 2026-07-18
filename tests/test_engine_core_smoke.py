from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas import AgentState, Flow, Script, Step
from tools.execution import execution_node


def test_engine_core_reports_missing_element():
    flow = Flow(
        id="smoke-flow",
        name="missing element smoke test",
        target_url="about:blank",
        steps=[],
    )
    script_code = """
def run(page):
    page.goto('about:blank')
    page.click('#does-not-exist')
"""
    state = AgentState(flow=flow, script=Script(flow_id=flow.id, code=script_code))
    updated = execution_node(state)
    result = updated.result
    assert result is not None
    assert result.status == "fail"
    assert result.error is not None
    assert result.error.kind == "missing_element"
