# Update Todos
- [x] Write harness/cases.py (F1 case matrix from C1+C2 data)
- [x] Write harness/runner.py (F1 pipeline runner with real execution node)
- [x] Write harness/metrics.py (F2 scoreboard table)
- [x] Write harness/verify.py (F3 healed-is-truly-healed check)
- [x] Write harness/regression_monitor.py (F3 bonus, only if ahead)
- [x] Run F1-F3 end-to-end and sanity check the scoreboard output
- [x] Lint harness/ with ruff

Epic F is built, all under /harness, ruff-clean, and run end-to-end for real against the pipeline.

# What's there:
- harness/cases.py (F1 data) — builds the {flow × break} case matrix directly from C1's CHECKOUT_FLOW baseline and C2's empirically-verified break_matrix.yaml.
- harness/runner.py (F1) — drives a LangGraph pipeline matching graph/build.py's exact shape (Discovery → ScriptGen → Execution → pass/give_up/diagnose → Repair → re-Execution loop) once per case. Writes harness/report.json.
- harness/metrics.py (F2) — aggregates the report into harness/report.md: auto-repair rate, per-failure-class breakdown, target check.
- harness/verify.py (F3) — before any case counts as "healed," independently re-runs it in a fresh browser context and checks it didn't short-circuit. Smoke-tested both ways (a real pass verifies true, a fabricated "healed" claim on a still-broken user gets caught and rejected).
- harness/regression_monitor.py **(F3 bonus)** — Pillow-based screenshot diff vs. a stored baseline, explicitly optional per the ticket.

**One important design call, flagged rather than hidden:** tools/execution.py (Engine's D3 file) currently hardcodes status="pass" as a stub. Importing it as-is would make every harness case trivially pass and the scoreboard meaningless. So runner.py wires its own copy of the graph with a **real** Playwright execution node (reusing the same harness.step_executor logic C1–C3 already proved live) instead of importing the stub — documented in the module docstring, with the one-line swap to make once D3 lands for real.

**Today's honest result:** running the full matrix gives 0% auto-repair (harness/report.md) — expected, since agents/diagnosis.py and agents/repair.py are still stubs that never actually change what gets executed, so every buggy case exhausts max_attempts=3 and gives up. That's the correct, non-fabricated number for the current state of the repo; it should climb once Healing lands real Diagnosis/Repair logic, with no changes needed in harness/.
