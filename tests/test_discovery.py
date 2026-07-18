"""Tests for the Flow Discovery agent (D1) — crawl, catalog, selection, break injection."""
from agents.discovery import (
    _default_tokens,
    build_catalog,
    crawl,
    discover_flow,
    discovery_node,
)
from schemas import AgentState


class FakePage:
    """Minimal stand-in that returns Swag Labs tokens for the crawl (no live browser)."""
    def __init__(self, tokens):
        self._tokens = list(tokens)

    def goto(self, *a, **k): pass
    def fill(self, *a, **k): pass
    def click(self, *a, **k): pass
    def eval_on_selector_all(self, *a, **k): return self._tokens


def test_crawl_collects_discovered_tokens():
    tokens = crawl(FakePage(_default_tokens()))
    assert "login-button" in tokens
    assert any(t.startswith("add-to-cart-") for t in tokens)


def test_catalog_has_two_smoke_and_five_e2e():
    catalog = build_catalog(_default_tokens())
    smoke = [f for f in catalog if f.id.startswith("smoke_")]
    e2e = [f for f in catalog if f.id.startswith("e2e_")]
    assert len(smoke) == 2 and len(e2e) == 5


def test_journey_omitted_when_elements_missing():
    # Drop the sort control — the sort journey must not appear.
    tokens = _default_tokens() - {"product-sort-container"}
    ids = {f.id for f in build_catalog(tokens)}
    assert "e2e_sort_inventory" not in ids


def test_discover_flow_selects_by_id():
    assert discover_flow("smoke_login").id == "smoke_login"


def test_break_injection_swaps_user():
    flow = discover_flow("e2e_checkout", user="problem_user")
    login = next(s for s in flow.steps if s.selector == '[data-test="username"]')
    assert login.value == "problem_user"


def test_unknown_flow_raises():
    try:
        discover_flow("does_not_exist")
    except KeyError:
        return
    raise AssertionError("expected KeyError")


def test_node_reads_flow_id_from_config():
    update = discovery_node(AgentState(), {"configurable": {"flow_id": "e2e_logout"}})
    assert update["flow"].id == "e2e_logout"
