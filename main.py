"""One clear entry point. Runs the self-healing pipeline once."""
from graph.build import build_graph
from schemas import AgentState


def run() -> None:
    app = build_graph()
    final = app.invoke(AgentState())
    print("pipeline complete:", final)


if __name__ == "__main__":
    run()
