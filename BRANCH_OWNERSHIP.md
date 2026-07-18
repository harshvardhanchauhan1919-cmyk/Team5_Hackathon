# Branch Ownership Map — who builds what, where

Four feature branches, one per pair. Everything branches off `develop` and merges back via PR.
Each branch below lists its **epics/tickets**, the **agents/components it builds**, the **files it owns**,
and its **dependencies** (what it needs from other branches, and what others need from it).

> **Golden rule:** you only edit files inside your branch's "Files you own" list. The one shared file —
> `schemas/__init__.py` — is frozen after hour 1 and changes only by a team call. If your ticket seems to
> need a schema change, raise it in the group, don't edit it solo.

---

## `feat/discovery_agent` — **Generation pair** (AI-B + Flex)

**The front of the pipeline: turn an intent into a runnable Playwright script.**

### Epics & tickets
- **A2** — OpenRouter config: `.env`, `models.yaml` role→model map, `model_for()` loader.
- **D1** — Flow Discovery agent (light, seeded flows).
- **D2** — Script Generator agent (Playwright script from a Flow).
- **D4** — Discovery + Script-Gen system prompts, kept stable for prompt caching.
- **H1** — README + local-run instructions (Docker cut; local `uv`/`pip` run only).

### Agents / components you develop
- **Flow Discovery agent** — decides which flow to automate; for the demo it seeds the Swag Labs
  login→cart→checkout→finish flow rather than truly auto-discovering. Output: a `Flow`.
- **Script Generator agent** — takes that `Flow` and emits a `Script` (Playwright Python code).
  This is the pair that calls `model_for("script_gen")` with the code model.

### Files you own
`agents/discovery.py` · `agents/script_gen.py` · `config/__init__.py` · `config/models.yaml` ·
`.env.example` · `README.md` · (prompt files you add under `agents/`)

### Depends on / provides
- **Needs:** the frozen `schemas` (Flow, Step, Script) and the LLM mock (`tools/mock_llm.py`) — both from hour 1.
- **Provides:** a working `Script` to the Engine's Execution node. This is on the **critical path** — Execution
  can't produce a real failure until Script-Gen is real, so land D1/D2 by ~9pm.

---

## `feat/engine_core` — **Engine pair** (AI-A + PM)

**The spine: the schema, the graph, the execution, and keeping `main` runnable.**

### Epics & tickets
- **A1** — Repo scaffold: monorepo layout, deps, CI (ruff + mocked-LLM tests + `playwright install`, <2 min). *(done)*
- **B1** — Freeze the typed state schema. **The single hard gate of the build.**
- **B2** — LangGraph graph: nodes, edges, the repair cycle, give-up-after-N.
- **D3** — Execution node: run the script + capture screenshots, video, trace, logs.
- **H2** — Demo/video direction, rehearsal, H14 feature-freeze + code-cleanup pass.
- Plus: **owns `main` and every integration merge** into `develop`→`main`.

### Agents / components you develop
- **The schema** (`schemas/__init__.py`) — Flow/Step/Script/RunResult/Error/Diagnosis/RepairAttempt/AgentState.
  You freeze it in hour 1; after that it's read-only for everyone.
- **The LangGraph graph** (`graph/build.py`) — wires all five nodes, defines the conditional edges
  (pass→END, fail→diagnose, capped→give-up), and the Repair→Execution loop.
- **Execution node** (`tools/execution.py`) — the only deterministic (no-LLM) node. Runs the Playwright
  script and captures artifacts. This is what produces the **real failure** the hero loop feeds on.

### Files you own
`schemas/__init__.py` (freeze, then read-only) · `graph/__init__.py` · `graph/build.py` ·
`tools/execution.py` · `main.py` · CI config (`.github/workflows/ci.yml`, `pyproject.toml`)

### Depends on / provides
- **Needs:** a `Script` from Generation to execute; the diagnosis/repair nodes from Healing to wire into the graph.
- **Provides:** the frozen contract + the graph skeleton that **everyone** builds against. You are the
  integration point — the 9pm convergence runs through this branch.

---

## `feat/healing_loop` — **Healing pair** (AI-C + UI)

**The hero loop and its visible story: diagnose the failure, repair the script, show it healing.**

### Epics & tickets
- **B3** — Deterministic LLM mock / fake-model interface, usable from hour 0. *(unblocks every lane)*
- **E1** — Error Diagnosis agent: classify + explain the 4 failure classes.
- **E2** — Adaptive Repair agent: rewrite the script, re-run, attempt cap. *(+ human-in-the-loop gate)*
- **E3** — Diagnosis/Repair prompt tuning — selector + timeout first (Flex pairs in here ~9pm).
- **F3** — "Healed is truly healed" verification hook (+ Regression Monitor, bonus, only if ahead).
- **G1** — Pipeline view: agent nodes with live pass/fail and the break→heal transition.
- **G2** — Artifact gallery: before/after-repair screenshots + video per run.
- **G3** — Visual polish pass (the "looking good" judging axis).

### Agents / components you develop
- **Error Diagnosis agent** — reads the failed `RunResult` and classifies it into selector / timeout /
  missing_element / flow_change, with a root cause + suggested fix. Calls `model_for("diagnosis")` (reasoning tier).
- **Adaptive Repair agent** — takes the `Diagnosis` and rewrites the `Script`, capped at N attempts.
  Calls `model_for("repair")` (reasoning tier). Also owns the **human-in-the-loop** gate on the repair→re-run edge.
- **The LLM mock** — the fake model returning canned typed responses so no one waits on prompts or burns credits.
- **The whole UI** — pipeline view + artifact gallery + polish.

### Files you own
`agents/diagnosis.py` · `agents/repair.py` · `tools/mock_llm.py` · `ui/` (all) ·
`harness/` verification hook for F3 (coordinate the file with Scoreboard so you don't collide)

### Depends on / provides
- **Needs:** the frozen `schemas`; a real failing `RunResult` from Execution (Engine) + the break matrix (Scoreboard)
  to have something real to diagnose. This is why all pairs converge at 9pm.
- **Provides:** the actual healing — the entire judged story — plus the UI that makes it visible.

---

## `feat/scoreboard_harness` — **Scoreboard pair** (QA-A + QA-B)

**The target and the numbers: Swag Labs, the break matrix, deterministic replay, and the metrics.**

### Epics & tickets
- **A3** — Standardize the coding tool + "hello browser" vs Swag Labs login, green on every machine.
- **C1** — Map Swag Labs flows (login → add-to-cart → checkout → finish) + document `data-test` selectors.
- **C2** — Break-user matrix: which login triggers which failure class (selector/timeout/missing/error).
- **C3** — HAR/trace recording + deterministic replay so CI and the demo don't depend on the live site.
- **E4** — Flow-change beat: reorder-checkout fixture (route-intercept or tiny local page).
- **F1** — Harness runner over `{flow × break}` cases.
- **F2** — Metrics table (≥50% auto-repair, classes healed) + scoreboard screenshots.

### Agents / components you develop
- **No LLM agents** — this lane owns the *test rig and the truth*. You build the harness that runs the whole
  pipeline over every `{flow × break-user}` combination, records auto-repair success, and prints the metrics table.
- **Break-user matrix** — empirically verified: log in as each buggy Swag Labs user and record which step breaks and how.
- **The flow-change fixture (E4)** — the one thing Swag Labs can't do (reorder a step), via Playwright route-intercept.

### Files you own
`harness/` (runner + metrics) · `fixtures/` (HAR recordings, flow-change fixture) ·
`hello_world/hello_browser.py` · Swag Labs selector/flow reference doc (add under `fixtures/` or repo root)

### Depends on / provides
- **Needs:** only "hello browser" to start — **no schema dependency**, so this lane starts at minute zero.
  Later needs the full pipeline (from Engine + Healing) to score.
- **Provides:** the break matrix (Healing needs it to diagnose), deterministic HAR replay (so CI + the demo
  don't hit the live site), and the metrics table that goes in the video and README.

---

## Quick reference — agent → branch

| Agent / component | Built on branch | Pair |
|---|---|---|
| Flow Discovery agent | `feat/discovery_agent` | Generation |
| Script Generator agent | `feat/discovery_agent` | Generation |
| OpenRouter `model_for()` config | `feat/discovery_agent` | Generation |
| Schema (frozen contract) | `feat/engine_core` | Engine |
| LangGraph graph + repair cycle | `feat/engine_core` | Engine |
| Execution node (Playwright, deterministic) | `feat/engine_core` | Engine |
| Error Diagnosis agent | `feat/healing_loop` | Healing |
| Adaptive Repair agent (+ human-in-the-loop) | `feat/healing_loop` | Healing |
| LLM mock | `feat/healing_loop` | Healing |
| UI (pipeline view, artifact gallery, polish) | `feat/healing_loop` | Healing |
| Harness + metrics scoreboard | `feat/scoreboard_harness` | Scoreboard |
| Break-user matrix + HAR replay | `feat/scoreboard_harness` | Scoreboard |
| Flow-change fixture | `feat/scoreboard_harness` | Scoreboard |

## The two collision risks to watch
1. **`schemas/__init__.py`** — touched by everyone conceptually, edited by Engine only, frozen after hour 1.
2. **`harness/`** — Scoreboard owns F1/F2; Healing owns the F3 verification hook. Put F3 in its own file
   (e.g. `harness/verify.py`) so the two pairs never edit the same file.
