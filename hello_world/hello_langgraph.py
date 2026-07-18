"""HELLO WORLD 2 — 'hello graph' (B4 walking skeleton).

Proves the LangGraph pipeline wires together end-to-end with the stub agents.
Run:  python hello_world/hello_langgraph.py
No LLM and no network needed — the stubs return canned typed state.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graph.build import build_graph
from schemas import AgentState


def main() -> None:
    app = build_graph()
    final = app.invoke(AgentState())
    # LangGraph returns a dict-like state; normalise for printing.
    result = final.get("result") if isinstance(final, dict) else final.result
    print("hello graph OK -> pipeline ran end-to-end")
    print("  final status:", getattr(result, "status", result))


if __name__ == "__main__":
    main()
