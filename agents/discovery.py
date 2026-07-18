"""Flow Discovery agent (D1) — Generation pair · branch feat/discovery_agent.

A real discovery agent: it crawls the live app to inventory what's there, assembles the
reachable user journeys into a catalog of test cases (smoke + e2e/regression), and freezes
that catalog to fixtures/flow_catalog.json. The pipeline then runs over the catalog.

Two stages
----------
1. crawl(page)            — deterministic DOM read: collect every [data-test] token. This is
                            the "eyes" — real and reproducible.
2. build_catalog(tokens)  — assemble journeys from what was discovered. A journey is emitted
                            only if the elements it needs were actually found on the site.

Runtime (inside the graph) reads the frozen catalog and selects one flow by id, re-injecting
the target user (that's how the "break" is switched) and URL. Nothing is hard-coded into the
node and nothing touches the frozen schema — category is carried by the flow-id convention
(smoke_* / e2e_*).
"""
from __future__ import annotations

import json
from pathlib import Path

from langchain_core.runnables import RunnableConfig

from schemas import AgentState, Flow, Step

DEFAULT_URL = "https://www.saucedemo.com/"
DEFAULT_USER = "standard_user"
DEFAULT_FLOW = "e2e_checkout"
_PASSWORD = "secret_sauce"
CATALOG_PATH = Path(__file__).parent.parent / "fixtures" / "flow_catalog.json"


# --------------------------------------------------------------------------- crawl
def crawl(page) -> set[str]:
    """Log in and walk the reachable pages, returning the discovered data-test tokens.

    Deterministic: it only reads the DOM. Uses standard_user so the crawl sees the full app.
    """
    def tokens_here() -> set[str]:
        return set(page.eval_on_selector_all(
            "[data-test]", "els => els.map(e => e.getAttribute('data-test'))"
        ))

    found: set[str] = set()
    page.goto(DEFAULT_URL, timeout=60_000)
    found |= tokens_here()                                   # login page
    page.fill('[data-test="username"]', DEFAULT_USER)
    page.fill('[data-test="password"]', _PASSWORD)
    page.click('[data-test="login-button"]')
    found |= tokens_here()                                   # inventory
    page.click('[data-test="shopping-cart-link"]')
    found |= tokens_here()                                   # cart
    return found


# ---------------------------------------------------------------- journey assembly
def _step(action: str, selector: str = "", value: str = "", description: str = "") -> Step:
    return Step(action=action, selector=selector, value=value, description=description)


def _login(user: str, url: str) -> list[Step]:
    return [
        _step("goto", value=url, description="open the site"),
        _step("fill", '[data-test="username"]', user, "username"),
        _step("fill", '[data-test="password"]', _PASSWORD, "password"),
        _step("click", '[data-test="login-button"]', description="log in"),
    ]


def _checkout_info() -> list[Step]:
    return [
        _step("click", '[data-test="checkout"]', description="start checkout"),
        _step("fill", '[data-test="firstName"]', "Jane", "first name"),
        _step("fill", '[data-test="lastName"]', "Doe", "last name"),
        _step("fill", '[data-test="postalCode"]', "12345", "zip"),
        _step("click", '[data-test="continue"]', description="continue"),
        _step("click", '[data-test="finish"]', description="finish order"),
        _step("expect_visible", '[data-test="complete-header"]', description="order complete"),
    ]


def _add(token: str) -> Step:
    item = token.replace("add-to-cart-", "")
    return _step("click", f'[data-test="{token}"]', item, f"add {item}")


def build_catalog(tokens: set[str], user: str = DEFAULT_USER, url: str = DEFAULT_URL) -> list[Flow]:
    """Assemble the catalog from discovered tokens. Each journey is included only if the
    elements it needs were found during the crawl.
    """
    adds = sorted(t for t in tokens if t.startswith("add-to-cart-"))
    catalog: list[Flow] = []

    def flow(fid: str, name: str, steps: list[Step]) -> Flow:
        return Flow(id=fid, name=name, target_url=url, steps=steps)

    open_cart = _step("click", '[data-test="shopping-cart-link"]', description="open cart")

    # --- smoke (2) ---
    if {"username", "password", "login-button"} <= tokens:
        catalog.append(flow(
            "smoke_login", "Smoke: login succeeds",
            _login(user, url) + [
                _step("expect_visible", '[data-test="shopping-cart-link"]',
                      description="inventory shown"),
            ],
        ))
    if adds and "shopping-cart-badge" in tokens:
        catalog.append(flow(
            "smoke_add_to_cart", "Smoke: add one item shows cart badge",
            _login(user, url) + [
                _add(adds[0]),
                _step("expect_visible", '[data-test="shopping-cart-badge"]',
                      description="cart badge appears"),
            ],
        ))

    # --- e2e / regression (5) ---
    if adds and "checkout" in tokens:
        catalog.append(flow(
            "e2e_checkout", "E2E: single-item checkout end to end",
            _login(user, url) + [_add(adds[0]), open_cart] + _checkout_info(),
        ))
    if len(adds) >= 2 and "checkout" in tokens:
        catalog.append(flow(
            "e2e_multi_item_checkout", "E2E: multi-item checkout with totals",
            _login(user, url) + [_add(adds[0]), _add(adds[1]), open_cart] + _checkout_info(),
        ))
    if "product-sort-container" in tokens:
        catalog.append(flow(
            "e2e_sort_inventory", "E2E: sort inventory by price low to high",
            _login(user, url) + [
                _step("select", '[data-test="product-sort-container"]', "lohi",
                      "sort price low->high"),
                _step("expect_visible", '[data-test="inventory-list"]',
                      description="inventory still shown"),
            ],
        ))
    if adds and "shopping-cart-link" in tokens:
        item = adds[0].replace("add-to-cart-", "")
        catalog.append(flow(
            "e2e_remove_from_cart", "E2E: add then remove item from cart",
            _login(user, url) + [
                _add(adds[0]),
                open_cart,
                _step("click", f'[data-test="remove-{item}"]', description="remove item"),
                _step("expect_visible", '[data-test="continue-shopping"]',
                      description="cart still usable"),
            ],
        ))
    if "logout-sidebar-link" in tokens:
        catalog.append(flow(
            "e2e_logout", "E2E: logout returns to login",
            _login(user, url) + [
                _step("click", "#react-burger-menu-btn", description="open menu"),
                _step("click", '[data-test="logout-sidebar-link"]', description="log out"),
                _step("expect_visible", '[data-test="login-button"]',
                      description="back at login"),
            ],
        ))
    return catalog


# --------------------------------------------------------------- catalog I/O + selection
def generate_catalog(page, path: Path = CATALOG_PATH) -> list[Flow]:
    """Crawl the live site, assemble the catalog, freeze it to disk."""
    catalog = build_catalog(crawl(page))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([f.model_dump() for f in catalog], indent=2))
    return catalog


def load_catalog(path: Path = CATALOG_PATH) -> list[Flow]:
    """Load the frozen catalog; if none exists yet, assemble the default Swag Labs catalog."""
    if path.exists():
        return [Flow(**d) for d in json.loads(path.read_text())]
    return build_catalog(_default_tokens())


def _inject(flow: Flow, user: str, url: str) -> Flow:
    """Re-point a catalog flow at a target user + URL (how the break is switched)."""
    steps = []
    for s in flow.steps:
        if s.action == "goto":
            steps.append(s.model_copy(update={"value": url}))
        elif s.selector == '[data-test="username"]':
            steps.append(s.model_copy(update={"value": user}))
        else:
            steps.append(s)
    return flow.model_copy(update={"steps": steps, "target_url": url})


def discover_flow(flow_id: str = DEFAULT_FLOW, user: str = DEFAULT_USER,
                  target_url: str = DEFAULT_URL) -> Flow:
    """Select one flow from the catalog by id and point it at the given user + URL."""
    catalog = load_catalog()
    for f in catalog:
        if f.id == flow_id:
            return _inject(f, user, target_url)
    raise KeyError(f"unknown flow '{flow_id}'. Known: {[f.id for f in catalog]}")


def discovery_node(state: AgentState, config: RunnableConfig) -> dict:
    """LangGraph node. Reads which flow/user/url from config; returns {"flow": ...}."""
    params = (config or {}).get("configurable", {})
    flow = discover_flow(
        flow_id=params.get("flow_id", DEFAULT_FLOW),
        user=params.get("user", DEFAULT_USER),
        target_url=params.get("target_url", DEFAULT_URL),
    )
    return {"flow": flow}


def _default_tokens() -> set[str]:
    """The Swag Labs element set used to seed the catalog offline (mirrors a real crawl)."""
    return {
        "username", "password", "login-button",
        "add-to-cart-sauce-labs-backpack", "add-to-cart-sauce-labs-bike-light",
        "shopping-cart-link", "shopping-cart-badge", "product-sort-container",
        "inventory-list", "checkout", "continue-shopping",
        "firstName", "lastName", "postalCode", "continue", "finish", "complete-header",
        "logout-sidebar-link",
    }
