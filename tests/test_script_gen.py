"""Tests for the Script Generator agent (D2)."""
import ast

from agents.discovery import discover_flow
from agents.script_gen import render_script, script_gen_node
from schemas import AgentState


def test_generated_code_is_valid_python():
    ast.parse(render_script(discover_flow("e2e_checkout")))


def test_generated_code_defines_run():
    ns: dict = {}
    exec(compile(render_script(discover_flow("e2e_checkout")), "<gen>", "exec"), ns)
    assert callable(ns.get("run"))


def test_run_issues_expected_playwright_calls():
    calls: list[tuple] = []

    class FakePage:
        def goto(self, url, **kw): calls.append(("goto", url))
        def fill(self, sel, val): calls.append(("fill", sel, val))
        def click(self, sel): calls.append(("click", sel))
        def select_option(self, sel, val): calls.append(("select", sel, val))
        def wait_for_selector(self, sel, **kw): calls.append(("wait", sel))

    ns: dict = {}
    exec(compile(render_script(discover_flow("e2e_checkout", user="standard_user")), "<g>", "exec"), ns)
    ns["run"](FakePage())
    assert calls[0] == ("goto", "https://www.saucedemo.com/")
    assert ("fill", '[data-test="username"]', "standard_user") in calls
    assert calls[-1] == ("wait", '[data-test="complete-header"]')


def test_select_action_renders():
    code = render_script(discover_flow("e2e_sort_inventory"))
    assert "page.select_option('[data-test=\"product-sort-container\"]', 'lohi')" in code


def test_node_produces_script_update():
    update = script_gen_node(AgentState(flow=discover_flow("smoke_login")))
    assert "def run(page):" in update["script"].code


def test_node_without_flow_raises():
    try:
        script_gen_node(AgentState())
    except ValueError:
        return
    raise AssertionError("expected ValueError")
