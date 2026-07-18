# Team Briefing — Self-Healing Browser Automation Agent

**Hackathon day · 3pm–7am (16h) · 8 people, 4 pairs · Coding tool: Claude Code (decided) · Credits: confirmed**

> **Source of truth: the PLAN, not the PRD.** The PLAN supersedes the PRD in two places: (1) team is 8, not 7; (2) target is **Swag Labs (saucedemo.com)** — we do NOT build our own demo site. The "break" is switching to a buggy login user, not a break toggle. Everything else (architecture, schema, model tiers, H14 freeze) carries over from the PRD.

## The one-paragraph pitch

Browser automation breaks when the UI changes. We build a system that, when a run fails, diagnoses *why*, rewrites its own Playwright script, and re-runs — no human debugging. The judged story is four beats: **run passes → we break it → system explains & repairs → re-run passes**, shown in a good-looking UI.

## Architecture in one line

LangGraph pipeline: `Discovery → ScriptGen → Execution → (pass → Report/UI | fail → Diagnosis → Repair → re-run, give up after N)`. LLM only for Discovery/Diagnosis/Repair; Playwright execution is deterministic. Everything communicates through one frozen typed schema (PLAN §11).

---

## The epics, what they actually mean

### Epic A — Setup & foundations *(the prerequisite epic — details below)*
Get every laptop green and the plumbing in place. Repo scaffold with uv + sub-2-min CI (A1, PM), OpenRouter config with the role→model map (A2, Flex), Claude Code standardized + "hello browser" against Swag Labs on every machine (A3, QA-B + PM). Nothing else can start honestly until this is done.

### Epic B — Shared contract & graph *(the gate)*
**B1 is the single hard gate of the night:** freeze the typed schema (Flow/Step/Script/RunResult/Error/Diagnosis/RepairAttempt) in hour 1, then never touch it without a team call. B2 (AI-A) builds the LangGraph graph with the repair cycle and give-up-after-N. B3 (AI-C) is the **LLM mock** — canned typed responses so every lane can build without burning credits or waiting on prompts; this is what decouples the four pairs. B4 (AI-B) is the walking skeleton: 6 stub nodes running end-to-end with a visible run, so `main` is demoable from hour 3.

### Epic C — Swag Labs target & break harness *(starts at minute zero)*
QA's lane; needs only "hello browser," not the schema. C1: map the checkout flow and capture the full `data-test` selector set (that's the baseline scripts are generated against). C2: the **break-user matrix** — empirically verify which buggy user (`problem_user`, `performance_glitch_user`, `error_user`, `locked_out_user`) triggers which failure class; run it, don't trust the docs. C3: HAR/trace recording + deterministic replay so CI and the recorded demo never depend on the live site.

### Epic D — Happy path agents
The front of the pipeline. D1: Flow Discovery, kept light — flows are seeded/hinted, not truly auto-discovered. D2: Script Generator (Flow → Playwright script). D3: Execution node — runs the script, captures screenshots/video/trace/logs (this is what produces the *real failure* the hero loop needs). D4: stable system prompts for Discovery/ScriptGen (stable = prompt caching = cheaper).

### Epic E — Hero loop *(the whole judged story)*
E1: Diagnosis agent — classify + explain the 4 failure classes (selector, timeout, missing element, flow change). E2: Adaptive Repair — rewrite the script, re-run, attempt cap. E3: prompt tuning, selector + timeout first (they're the easiest wins toward ≥50% auto-repair). E4: the **flow-change beat** — Swag Labs' buggy users don't reorder steps, so one tiny local fixture or Playwright route-intercept covers that one failure class.

### Epic F — Harness, scoreboard & metrics *(the proof)*
F1: harness runner over `{flow × break}` cases. F2: the metrics table showing ≥50% auto-repair and which classes healed — this is the scoreboard that goes in the video and README. F3: "healed is truly healed" verification (a repair that passes for the wrong reason is a demo-killer) + Regression Monitor **only if ahead**.

### Epic G — UI *(the "looking good" axis)*
G1: pipeline view — agent nodes lighting up pass/fail, the break→heal transition visible live. G2: artifact gallery — before/after-repair screenshots and video per run. G3: polish pass. UI builds against the mock (B3) from the skeleton onward, so it never waits on real agents.

### Epic H — Demo, docs & ship
H1: README + one-command `docker compose up`. H2: PM directs the video, runs rehearsal, and enforces the **H14 feature freeze (5am)** — no new features after that, period.

## Dependencies — the shape of the night

- **Gate:** B1 schema freeze (hour 1) blocks nearly every typed ticket.
- **Critical path:** A → B1 → B4 skeleton → D (Execution producing a real failure) → E hero loop → F metrics → record. This chain decides whether we finish.
- **Parallel tracks:** C starts immediately (no schema needed); G branches off the skeleton against the mock.
- **The convergence to watch (~9pm–1am):** the hero loop needs Execution (D), the break matrix (C), and Diagnosis/Repair (E) simultaneously. If C or D is late, the loop can't become real — and the loop is the entire judged story. All four pairs present for that window.

---

## Epic A prerequisites — do these first

**Before anything else (each person):**

1. **Claude Code installed and authenticated** — everyone, verified by running one trivial prompt.
2. **Python 3.12+ and uv installed**, `uv --version` works.
3. **Playwright + Chromium:** `uv add playwright && playwright install chromium`.
4. **GitHub access:** everyone can clone/push to the repo; PM sets branch protection.
5. **OpenRouter key distributed** (one key, `.env`, never committed — `.gitignore` from commit #1). Credit ceiling is confirmed, so the tier map in PLAN §12 stands.
6. **Docker Desktop installed** (needed for H1's `docker compose up`; install now, not at 5am).

**Epic A tickets, in order:**

- **A1 (PM):** monorepo scaffold — `schemas / graph / agents / tools / ui / harness / tests / fixtures`, `uv init`, deps, push, CI = ruff + mocked-LLM tests + `playwright install`, kept under 2 minutes.
- **A2 (Flex):** `.env` + `models.yaml` role→model map + `model_for()` loader + a 5-line smoke test that prints a model reply.
- **A3 (QA-B + PM):** "hello browser" — log into saucedemo.com as `standard_user`, add the backpack, checkout, screenshot each step. **Every laptop must run this green.**

**Definition of done for hour 1 (4pm):** CI green on `main` · every laptop runs the Swag Labs happy path with screenshots · schema (B1) frozen and merged · LLM mock (B3) in · stub graph (B4) running · break matrix (C2) drafted. Then split into lanes.

## Kickoff — the first hour, all 8 together

Decide in the first 10 minutes: ~~coding tool~~ (Claude Code ✓), ~~credit ceiling~~ (✓), and **the exact demo flow + which buggy users go in the video** (last open item from PLAN §14).

Then in parallel, per PLAN §8: PM → repo (A1) · Flex → OpenRouter smoke test (A2) · QA-A → hello browser, everyone runs it (A3) · AI-A → drive schema freeze, all review (B1) · AI-C → mock LLM (B3) · AI-B → walking skeleton (B4) · QA-B → break-matrix spike (C2).

## Distribution before dispersing (4pm)

| Pair | People | Epics owned | First ticket after kickoff |
|---|---|---|---|
| **Engine** | AI-A + PM | B (graph), D3, H2, integration | B2 graph + repair cycle |
| **Generation** | AI-B + Flex | D1, D2, D4, A2, H1 | D1/D2 against the mock |
| **Healing** | AI-C + UI | E1–E3, B3, F3, G1–G3 | E1 Diagnosis against the mock; UI starts G1 off the skeleton |
| **Scoreboard** | QA-A + QA-B | C1–C3, E4, F1, F2 | Finish C2 matrix, start C1 selector baseline |

Sync points: **9pm convergence** (hero loop integration, all pairs) and **5am freeze** (record + clean). Light sleep rotation so 1–2 people are fresh at 5am.

## Non-negotiables

Temperature 0 everywhere · no `:free` models in the recorded demo · reasoning tier (Sonnet) only for Diagnosis + Repair · tiny PRs, PM owns `main` · schema changes require a team call · **feature freeze at hour 14 (5am)**.
