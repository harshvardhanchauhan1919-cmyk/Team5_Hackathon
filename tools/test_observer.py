"""Interactive Self-Healing Observer (manual testing utility).

Simulates a failing Playwright execution and steps through the diagnosis,
repair, and verification stages in the terminal with safe ASCII printing.
"""
from __future__ import annotations

import os
import sys
import time

# Ensure we can import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.diagnosis import diagnosis_node
from agents.repair import repair_node
from harness.verify import verify_healed
from schemas import AgentState, Error, RunResult, Script


def main():
    # Force mock mode for deterministic offline run
    os.environ["USE_MOCK"] = "1"

    # Use rich for visual colors if available, fall back to standard print
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax
        console = Console()
    except ImportError:
        class SimpleConsole:
            def print(self, msg, *args, **kwargs):
                print(msg)
            def rule(self, title):
                print(f"\n=== {title} ===")
        console = SimpleConsole()
        Panel = lambda content, title, border_style=None: f"[{title}]\n{content}"
        Syntax = lambda code, lang, theme=None: code

    try:
        console.rule("Starting Self-Healing Loop Observer")
    except UnicodeEncodeError:
        # Fallback to standard prints if console encoding is restrictive
        class SafeConsole:
            def print(self, msg, *args, **kwargs):
                # Strip basic brackets/tags
                clean_msg = str(msg).replace("[bold yellow]", "").replace("[/bold yellow]", "")
                clean_msg = clean_msg.replace("[bold red]", "").replace("[/bold red]", "")
                clean_msg = clean_msg.replace("[red]", "").replace("[/red]", "")
                clean_msg = clean_msg.replace("[bold green]", "").replace("[/bold green]", "")
                print(clean_msg)
            def rule(self, title):
                print(f"\n=== {title} ===")
        console = SafeConsole()
        Panel = lambda content, title, border_style=None: f"[{title}]\n{content}"
        Syntax = lambda code, lang, theme=None: code
        console.rule("Starting Self-Healing Loop Observer")
    
    # ------------------------------------------------------------------
    # Step 1: Initial failed script state
    # ------------------------------------------------------------------
    initial_script = Script(
        flow_id="swag_labs_checkout",
        code=(
            "from playwright.sync_api import sync_playwright\n"
            "def run():\n"
            "    # Navigate and check out\n"
            "    page.click('[data-test=\"checkout-btn-renamed\"]') # Fails here\n"
        )
    )

    failed_result = RunResult(
        script_id="swag_labs_checkout",
        status="fail",
        logs=(
            "Navigating to Cart\n"
            "Error: locator.click: Timeout 5000ms exceeded waiting for selector [data-test='checkout-btn-renamed']"
        ),
        screenshots=["error_screenshot.png"],
        error=Error(
            kind="selector",
            message="Timeout waiting for selector [data-test='checkout-btn-renamed']",
            step_index=4
        )
    )

    state = AgentState(
        script=initial_script,
        result=failed_result,
    )

    console.print("\n[bold yellow]Step 1: Simulating Failed Playwright Run[/bold yellow]")
    console.print(f"Error kind: [bold red]{state.result.error.kind}[/bold red]")
    console.print(f"Error message: [red]{state.result.error.message}[/red]")
    time.sleep(1)

    # ------------------------------------------------------------------
    # Step 2: Trigger Diagnosis Agent
    # ------------------------------------------------------------------
    console.rule("Running Error Diagnosis Node")
    state = diagnosis_node(state)
    
    diag_details = (
        f"Root Cause: {state.diagnosis.root_cause}\n"
        f"Confidence: {state.diagnosis.confidence * 100:.1f}%\n"
        f"Suggested Fix: {state.diagnosis.suggested_fix}"
    )
    try:
        console.print(Panel(diag_details, title="Diagnosis Result", border_style="cyan"))
    except Exception:
        console.print(diag_details)
    time.sleep(1.5)

    # ------------------------------------------------------------------
    # Step 3: Trigger Repair Agent
    # ------------------------------------------------------------------
    console.rule("Running Adaptive Repair Node")
    state = repair_node(state)
    
    console.print("\n[bold green]Repaired Script Output:[/bold green]")
    try:
        syntax_code = Syntax(state.script.code, "python", theme="monokai")
        console.print(syntax_code)
    except Exception:
        console.print(state.script.code)
    time.sleep(1.5)

    # ------------------------------------------------------------------
    # Step 4: Verification Hook
    # ------------------------------------------------------------------
    console.rule("Running Verification Hook")
    
    # Simulate a passing run result on the repaired code
    healed_result = RunResult(
        script_id="swag_labs_checkout",
        status="pass"
    )
    
    is_verified = verify_healed(healed_result, original_result=failed_result)
    
    if is_verified:
        console.print("\n[bold green]SUCCESS: Script healing verified and confirmed passed! No regressions.[/bold green]\n")
    else:
        console.print("\n[bold red]FAILURE: Verification hook failed to validate the repair.[/bold red]\n")


if __name__ == "__main__":
    main()
