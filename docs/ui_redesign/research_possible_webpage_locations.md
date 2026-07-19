# Research — possible webpage locations (input / control / output)

This catalogs every place in the codebase where, logically, a webpage could reasonably:
request **user input**, let a user **enforce control** over behavior, or **present output**
back to a user. Today only [ui/app.py](ui/app.py) and its two components actually render a
page (see [research_existing_webpages.md](research_existing_webpages.md)); everything else
below is either (a) already wired to that one dashboard, (b) exposed only as an env var /
CLI arg / function default today, or (c) currently hardcoded with no user-facing surface at
all — each entry is labeled accordingly so this doubles as a gap list for extending the UI.

Categories: **Input** (data a user supplies), **Control** (a choice/gate/threshold that changes
behavior), **Output** (something meant to be read by a user).

---

## 1. User input

| # | File : Line | What | Surface today |
|---|---|---|---|
| 1 | [config/__init__.py:15-16](config/__init__.py#L15-L16) | `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` read from env | `.env` file only — no UI field |
| 2 | [config/models.yaml](config/models.yaml) | Role→model map (`discovery`, `script_gen`, `diagnosis`, `repair`, `dev_default`) | Hand-edited YAML file — no UI |
| 3 | [.env.example:6-7](.env.example#L6-L7) | `USE_MOCK`, `HITL` env flags a user sets before launch | `.env` file only |
| 4 | [ui/app.py:60-64](ui/app.py#L60-L64) | **Operation Mode** dropdown ("Mock State Player" / "Live Graph Execution") | ✅ rendered — sidebar selectbox |
| 5 | [ui/app.py:80-89](ui/app.py#L80-L89) | **Select Execution Stage** radio (which of the 4 canned mock states to view) | ✅ rendered — sidebar radio |
| 6 | [agents/discovery.py:205-213](agents/discovery.py#L205-L213) | `discovery_node`'s `config["configurable"]`: `flow_id`, `user`, `target_url` — literally the fields a "pick a flow / pick a break-user" form would submit | Only reachable via `graph.invoke(state, config=...)` in code (e.g. [harness/cases.py:37-43](harness/cases.py#L37-L43), [tests/test_discovery.py:62](tests/test_discovery.py#L62)) — **no UI surface at all** |
| 7 | [harness/replay.py:87](harness/replay.py#L87) | `sys.argv[1]` — `record` vs `verify` subcommand | CLI only |
| 8 | [harness/break_matrix.py:24-30](harness/break_matrix.py#L24-L30) | `USERS` list — which Swag Labs accounts to probe, `PASSWORD` | Hardcoded Python list — no UI |
| 9 | [harness/regression_monitor.py:41](harness/regression_monitor.py#L41) | `threshold` — how sensitive the screenshot-diff regression check is | Function default only — no UI/CLI |

---

## 2. User control (behavior-altering toggles / gates / thresholds)

| # | File : Line | What | Surface today |
|---|---|---|---|
| 1 | [ui/app.py:66](ui/app.py#L66) | **HITL checkbox** ("Enable Human-in-the-Loop Gate") — sets `state.hitl` | ✅ rendered checkbox, **but the gate it should control is unimplemented** — see #7 |
| 2 | [ui/app.py:67-72](ui/app.py#L67-L72) | **Max Healing Attempts** number input — sets `state.max_attempts` (give-up-after-N) | ✅ rendered — sidebar number input |
| 3 | [ui/app.py:111](ui/app.py#L111) | **"Run Live Pipeline" button** — the one control that actually triggers a real `graph.build.build_graph()` invocation instead of replaying a mock | ✅ rendered button |
| 4 | [graph/build.py:19-24](graph/build.py#L19-L24) `_after_execution` | The pass / give-up / diagnose routing decision (`state.max_attempts` cap) | Enforced in code; the cap value itself is user-set via #2 above, but the routing logic itself has no on/off switch |
| 5 | [graph/build.py:44](graph/build.py#L44) + [agents/repair.py:6-7](agents/repair.py#L6-L7) | **TODO: human-in-the-loop `interrupt()`** on the Repair→Execution edge — this is the actual gate the HITL checkbox (#1) is supposed to control | **Not implemented** — `TESTING_HEALING_LOOP.md:103` documents the intended "pause, show diff, click Proceed" UX, but no `interrupt()` call exists in `graph/build.py` yet, so toggling the checkbox currently has no runtime effect |
| 6 | [schemas/__init__.py:72-73](schemas/__init__.py#L72-L73) | `AgentState.max_attempts` / `AgentState.hitl` — the two knobs both controls above ultimately set | Backing fields; already schema-frozen |
| 7 | [config/__init__.py:24-32](config/__init__.py#L24-L32) `model_for()` | `USE_MOCK` env var — global real-LLM vs. deterministic-mock switch | Env var only; no UI toggle equivalent to the `.env.example` comment's promise |
| 8 | [tools/execution.py:56](tools/execution.py#L56) | `headless=True` hardcoded in the real Execution node | **Not configurable anywhere** — no CLI flag, no UI toggle, no env var |
| 9 | [harness/runner.py:28](harness/runner.py#L28), [harness/runner.py:61](harness/runner.py#L61) | `headless` parameter threaded through the harness runner | Function default only — no CLI/UI exposure |
| 10 | [harness/step_executor.py:21-23](harness/step_executor.py#L21-L23), [harness/step_executor.py:102](harness/step_executor.py#L102) | `ACTION_TIMEOUT_MS`, `GOTO_TIMEOUT_MS`, `SLOW_STEP_THRESHOLD_S`, `GRACE_TIMEOUT_MS` — the timing thresholds that decide `selector` vs `timeout` classification | Hardcoded module constants — no override surface |
| 11 | [harness/regression_monitor.py:19](harness/regression_monitor.py#L19) | `DEFAULT_THRESHOLD = 0.05` — regression-monitor sensitivity | Hardcoded, with an explicit code comment flagging it should be tuned later |

---

## 3. Output presentation

| # | File : Line | What | Surface today |
|---|---|---|---|
| 1 | [ui/components/pipeline.py](ui/components/pipeline.py) (whole file) | 5-node pipeline status visualization | ✅ rendered — `st.html()` |
| 2 | [ui/components/gallery.py:14-41](ui/components/gallery.py#L14-L41) | Failure + Diagnosis report panel (error kind/message/step, root cause, confidence, suggested fix) | ✅ rendered |
| 3 | [ui/components/gallery.py:44-64](ui/components/gallery.py#L44-L64) | Script Code View tabs — current script vs. every repair attempt's script | ✅ rendered — `st.code` |
| 4 | [ui/components/gallery.py:66-97](ui/components/gallery.py#L66-L97) | Screenshot gallery grid | ✅ rendered, but shows a `placehold.co` placeholder rather than the real PNG on disk (see `research_existing_webpages.md`) |
| 5 | [ui/components/gallery.py:99-110](ui/components/gallery.py#L99-L110) | Execution Logs tab — original run + every repair attempt's raw log text | ✅ rendered — `st.code` |
| 6 | [main.py:41-71](main.py#L41-L71) | CLI run summary — status, repair attempt count, screenshot/trace paths, last error, final `PASS`/`FAIL`/`HEALED` line, process exit code | Terminal only — no web surface |
| 7 | [tools/execution.py:17-22](tools/execution.py#L17-L22), [tools/execution.py:99](tools/execution.py#L99) | `LOGGER` (`[ENGINE_CORE]`-prefixed) execution-failure logging | Terminal/log file only |
| 8 | [agents/diagnosis.py:78-85](agents/diagnosis.py#L78-L85) | Diagnosis success/parse-failure logging | Terminal/log file only |
| 9 | [agents/repair.py:65-68](agents/repair.py#L65-L68) | Repair attempt success/failure logging | Terminal/log file only |
| 10 | [harness/selectors.py:88-104](harness/selectors.py#L88-L104), [harness/selectors.py:108](harness/selectors.py#L108) | C1 baseline verification — writes `harness/selectors.md` (a markdown table) and prints a summary line | File + terminal — no web surface |
| 11 | [harness/break_matrix.py:66-84](harness/break_matrix.py#L66-L84) | C2 break-user probe progress + final per-user classification table, plus `harness/break_matrix.yaml` | File + terminal — no web surface |
| 12 | [harness/replay.py:64-94](harness/replay.py#L64-L94) | C3 HAR record/verify progress and per-case `replay=... expected=... -> OK/MISMATCH` lines | Terminal only |
| 13 | [harness/runner.py:65-78](harness/runner.py#L65-L78) | F1 per-case run progress (`initial=`, `final=`, `healed=`, `verified=`) + `harness/report.json` | File + terminal — no web surface |
| 14 | [harness/metrics.py:93-99](harness/metrics.py#L93-L99) | **F2 scoreboard** — the headline auto-repair rate, target met/not-met, and `harness/report.md` — arguably the single most important number in the whole project (README/video hero metric) | File + terminal only — **not surfaced in the Streamlit dashboard at all** |
| 15 | [harness/regression_monitor.py:58-63](harness/regression_monitor.py#L58-L63) | Per-user regression diff ratio + ok/REGRESSED verdict | Terminal only |
| 16 | [tools/test_observer.py:108-163](tools/test_observer.py#L108-L163) | Rich-formatted terminal walkthrough of a full diagnose→repair→verify cycle (colored panels, syntax-highlighted code) | Terminal only (falls back to plain `print` if `rich` isn't installed) — effectively a second, unrendered UI |
| 17 | [tools/engine_core_smoke_test.py:64-65](tools/engine_core_smoke_test.py#L64-L65) | Smoke-test pass confirmation + full `RunResult` JSON dump | Terminal only |

---

## Notable gaps this surfaces

- **The F2 scoreboard (item 14) has no web presence.** It's the number the whole hackathon is judged on, yet it only exists as a generated `.md`/`.json` file and terminal print — the Streamlit dashboard has no scoreboard tab at all today.
- **The HITL checkbox is disconnected from its gate** (control items 1 and 5): the UI element exists and sets `state.hitl`, but `graph/build.py` never reads it — there's no `interrupt()` on the Repair→Execution edge yet, so checking the box currently changes nothing at runtime.
- **Discovery's `flow_id`/`user`/`target_url` selection (input item 6) has zero UI surface** — every current caller (harness, tests) sets it in Python via `config=`. A "pick a flow" / "pick a break-user" dropdown pair would be the natural UI counterpart to what `harness/cases.py` already does programmatically.
- **`headless` is hardcoded `True` in the real Execution node** (control item 8) — useful for CI/demo determinism, but there's no way for an operator to watch the browser live even if they wanted to, unlike `hello_world/hello_browser.py`'s comment (`# set headless=False to watch it`) which only applies to that standalone script.
