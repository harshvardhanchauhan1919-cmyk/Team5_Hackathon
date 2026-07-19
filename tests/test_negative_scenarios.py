"""Negative / regression tests: break injection, and F3 rejecting false heals.

Browser-free by design — these exercise the injection and guard logic, not live
Playwright. The live browser paths are covered by the harness runner.
"""
from agents.discovery import _corrupt_selector, discover_flow, discovery_node
from agents.script_gen import render_script
from harness.cases import SELECTOR_BREAK_CASE, Case
from harness.verify import verify_healed_live
from schemas import AgentState, RunResult, Script

BREAK_USERS = ["problem_user", "performance_glitch_user", "error_user", "locked_out_user"]
USERNAME_SEL = '[data-test="username"]'


def _login_value(flow):
    return next(s.value for s in flow.steps if s.selector == USERNAME_SEL)


def test_every_break_user_is_injected_into_login():
    for user in BREAK_USERS:
        assert _login_value(discover_flow("e2e_checkout", user=user)) == user


def test_corrupt_selector_breaks_only_the_target():
    target = '[data-test="add-to-cart-sauce-labs-backpack"]'
    broken = _corrupt_selector(discover_flow("e2e_checkout"), target)
    selectors = [s.selector for s in broken.steps]
    assert target not in selectors
    assert '[data-test="add-to-cart-sauce-labs-backpack-BROKEN"]' in selectors
    assert USERNAME_SEL in selectors  # unrelated steps untouched


def test_discovery_node_applies_break_selector_from_config():
    config = {"configurable": {"break_selector": '[data-test="checkout"]'}}
    flow = discovery_node(AgentState(), config)["flow"]
    assert any(s.selector == '[data-test="checkout-BROKEN"]' for s in flow.steps)


def test_broken_flow_renders_a_broken_script():
    config = {"configurable": {"break_selector": '[data-test="add-to-cart-sauce-labs-backpack"]'}}
    flow = discovery_node(AgentState(), config)["flow"]
    assert "add-to-cart-sauce-labs-backpack-BROKEN" in render_script(flow)


def test_selector_break_case_config():
    configurable = SELECTOR_BREAK_CASE.config()["configurable"]
    assert configurable["user"] == "standard_user"
    assert configurable["break_selector"] == '[data-test="add-to-cart-sauce-labs-backpack"]'


def test_user_break_case_has_no_break_selector():
    case = Case(id="x", user="problem_user", expected_kind="selector")
    assert "break_selector" not in case.config()["configurable"]


def _healed_state(login_user, script_user, status="pass"):
    state = AgentState(flow=discover_flow("e2e_checkout", user=login_user))
    state.repair_attempts.append(1)  # non-empty: a repair happened
    state.result = RunResult(script_id="e2e_checkout", status=status)
    state.script = Script(
        flow_id="e2e_checkout",
        code=f'def run(page):\n    page.fill("{USERNAME_SEL}", "{script_user}")\n',
    )
    return state


def test_verify_rejects_when_no_repair_happened():
    state = _healed_state("standard_user", "standard_user")
    state.repair_attempts.clear()
    assert verify_healed_live(state).verified is False


def test_verify_rejects_non_pass_status():
    state = _healed_state("standard_user", "standard_user", status="fail")
    assert verify_healed_live(state).verified is False


def test_verify_rejects_credential_switch():
    # locked_out flow, but the repaired script logs in as standard_user — a cheat.
    result = verify_healed_live(_healed_state("locked_out_user", "standard_user"))
    assert result.verified is False
    assert "credential switch" in result.reason
