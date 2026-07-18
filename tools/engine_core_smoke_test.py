"""Standalone smoke test for the engine-core execution node.

This script runs without the other sub-agents and verifies that execution
returns a structured result for a flow with a missing element.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schemas import AgentState, Flow, Script, Step
from tools.execution import execution_node


def build_sample_page(path: Path) -> None:
    html = textwrap.dedent(
        """
        <!doctype html>
        <html>
          <body>
            <h1>Engine core smoke test</h1>
            <form>
              <input id="username" />
              <button id="submit">Submit</button>
            </form>
          </body>
        </html>
        """
    ).strip()
    path.write_text(html, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        page_path = Path(tmpdir) / "page.html"
        build_sample_page(page_path)
        flow = Flow(
            id="smoke-flow",
            name="missing element smoke test",
            target_url=page_path.as_uri(),
            steps=[
                Step(action="goto", value=page_path.as_uri(), description="open page"),
                Step(action="fill", selector="#username", value="demo"),
                Step(action="click", selector="#does-not-exist", description="missing button"),
            ],
        )
        state = AgentState(flow=flow, script=Script(flow_id=flow.id, code=""))
        updated = execution_node(state)
        result = updated.result
        if result is None:
            raise SystemExit("execution_node did not produce a result")
        if result.status != "fail" or result.error is None or result.error.kind != "missing_element":
            raise SystemExit(f"unexpected result: {result.model_dump()}")
        print("engine_core smoke test passed")
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
