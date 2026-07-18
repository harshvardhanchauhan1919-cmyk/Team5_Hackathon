"""Flow Discovery agent (D1) — Generation pair · branch feat/discovery_agent.

Light for the demo: flows are seeded/hinted rather than fully auto-discovered.
"""
from __future__ import annotations

from schemas import AgentState, Flow, Step


def discovery_node(state: AgentState) -> AgentState:
    # TODO(Generation): replace stub with seeded-flow logic (optionally LLM-assisted).
    if state.flow is None:
        state.flow = Flow(
            id="swaglabs_checkout",
            name="Login -> add to cart -> checkout -> finish",
            target_url="https://www.saucedemo.com/",
            steps=[
                Step(action="goto", value="https://www.saucedemo.com/", description="open site"),
                Step(action="fill", selector='[data-test="username"]', value="standard_user"),
                Step(action="fill", selector='[data-test="password"]', value="secret_sauce"),
                Step(action="click", selector='[data-test="login-button"]'),
                Step(action="click", selector='[data-test="add-to-cart-sauce-labs-backpack"]'),
                Step(action="click", selector='[data-test="shopping-cart-link"]'),
                Step(action="click", selector='[data-test="checkout"]'),
            ],
        )
    return state
