# Team5 — Self-Healing Browser Automation Agent

When a browser automation run fails, the system diagnoses *why*, rewrites its own Playwright script (adapting to changed flows), and re-runs — no human debugging. Built on **LangGraph** + **Playwright**. Diagnosis/repair can run through **OpenRouter**, a headless **opencode** CLI session, or a headless **claude** CLI session — pick one with `LLM_BACKEND` (see [Run modes](#running-the-pipeline--run-modes)). Targets: the live **Swag Labs** demo (saucedemo.com) and a local **test_website** clone you can genuinely break on demand.

---

## 1. One-time setup → Hello World

Do this on every laptop before we split into lanes. Two Hello Worlds must go green: **hello browser** (Playwright works) and **hello graph** (the LangGraph pipeline wires end-to-end).

### Prerequisites (install these first)

- **Python 3.12+** — check: `python --version`
- **Git** — check: `git --version`
- **Claude Code** — our standardized coding tool, installed + authenticated
- A **GitHub account** with access to this repo

### Step-by-step

```bash
# 1. Clone the repo and enter it
git clone <REPO_URL> Team5_Hackathon
cd Team5_Hackathon

# 2. Get onto the integration branch (we branch off develop, never main)
git checkout develop
git pull origin develop

# 3. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install the browser Playwright drives (Chromium only — fast)
playwright install chromium

# 6. Set up your environment file (never commit .env — it's gitignored)
cp .env.example .env        # Windows: copy .env.example .env
#   defaults to USE_MOCK=1 (no network, no key needed) so the steps below work
#   out of the box. To run a real LLM, see "Run modes" below.

# 7. HELLO WORLD 1 — hello browser (proves Playwright + the target site work)
python hello_world/hello_browser.py
#   -> prints "hello browser OK" and drops screenshots in hello_world/artifacts/

# 8. HELLO WORLD 2 — hello graph (proves the LangGraph skeleton runs end-to-end)
python hello_world/hello_langgraph.py
#   -> prints "hello graph OK -> pipeline ran end-to-end"

# 9. Run the tests (LLM is mocked — no network, no credits burned)
pytest -q
```

**You are ready when:** both Hello Worlds print OK and `pytest` is green. From here every pair works independently on its own feature branch.

> `python` not found? Try `python3`. On Windows, "cannot be loaded because running scripts is disabled" → run
> `Set-ExecutionPolicy -Scope Process RemoteSigned` then re-activate.

---

## 2. Running the pipeline — run modes

`config/__init__.py:model_for()` is the one place diagnosis/repair pick a model. It reads
two env vars from `.env`:

| `USE_MOCK` | `LLM_BACKEND` | What runs | Needs |
|---|---|---|---|
| `1` | *(ignored)* | `tools/mock_llm.py` — canned, deterministic responses | nothing |
| `0`/unset | `api` *(default)* | OpenRouter via `langchain_openai.ChatOpenAI`, model per `config/models.yaml` | `OPENROUTER_API_KEY` in `.env` |
| `0`/unset | `opencode` | headless `opencode run` CLI (`tools/opencode_llm.py`) | `opencode` on `PATH`, already authenticated |
| `0`/unset | `claude` | headless `claude -p` CLI (`tools/claude_llm.py`) | `claude` on `PATH`, already authenticated |

`USE_MOCK=1` always wins — it's the deterministic path tests and CI depend on, not a
fourth "real" backend. Pick one of the three real backends with whichever CLI/key you
actually have on the machine; all three implement the same `model.invoke(messages)`
shape, so nothing else in the pipeline needs to know which one is active.

```bash
# deterministic, no network — this is the default after `cp .env.example .env`
USE_MOCK=1 python main.py

# real LLM, no API key needed — uses whatever `opencode` is authenticated with
LLM_BACKEND=opencode python main.py
#   model defaults to OPENCODE_MODEL=github-copilot/gpt-5.5; override in .env

# real LLM, no API key needed — uses this machine's authenticated `claude` login
LLM_BACKEND=claude python main.py
#   model defaults to CLAUDE_MODEL=sonnet; override in .env

# real LLM via OpenRouter — needs OPENROUTER_API_KEY set in .env
LLM_BACKEND=api python main.py
```

Every real backend also logs its raw prompt/response pairs to
`artifacts/opencode_headless/` or `artifacts/claude_headless/` (one JSON file per call) —
useful evidence when you want to see exactly what the model was shown and what it said.

The same `LLM_BACKEND=...` prefix works in front of any script in this repo:
`python main.py`, `python -m harness.runner`, `python -m harness.test_website_runner`,
`python -m tools.run_flow_case <case_id> --verify`.

### Targets: saucedemo vs. the local test_website

The pipeline is target-agnostic — every `Flow` carries its own `target_url`, injected via
`config={"configurable": {"target_url": ..., "user": ..., "flow_id": ...}}` (see
`harness/cases.py:Case.config()`). Two case matrices exist:

- **`harness/cases.py`** — the live Swag Labs site. Its one "healable" break
  (`SELECTOR_BREAK_CASE`) works by mangling a selector *the pipeline already knows is
  correct*, since saucedemo.com itself can't be changed on demand — useful for a fast
  sanity check, not for testing real diagnosis.
- **`harness/test_website_cases.py`** — a local Vite/React clone of Swag Labs
  (`test_website/`) that can be **genuinely** broken with a `?break=<mode>` query
  param (real `data-test` renames served by the app itself), so the healing loop has
  to actually diagnose a live DOM change, not reverse a known mutation. Start it first:

  ```bash
  cd test_website && npm install && npm run dev   # http://localhost:3000
  ```

  Then, from the repo root, in another terminal:

  ```bash
  LLM_BACKEND=opencode python -m harness.test_website_runner
  #   -> harness/report_test_website.json + .md, screenshots in artifacts/engine_core/
  ```

  See `test_website/README.md` for the full list of break modes.

---

## 3. Do we need Docker? No.

**We run everything locally — no Docker image.** Playwright ships its own browser binaries via `playwright install chromium`, so there's nothing to containerize for the demo. Docker was in the original PRD only to bundle a self-built demo site; since we target the live Swag Labs site, that reason is gone.

- **Local run:** the setup above is the whole story. `python main.py` runs the pipeline.
- **MCP:** not needed for testing. We drive the browser directly through Playwright's own API (deterministic and fast); an MCP browser server would add a moving part we don't need under the time crunch.
- **Determinism for CI + the recorded demo:** instead of Docker, we record a **HAR/trace** of Swag Labs (ticket C3) and replay it, so runs don't depend on the live network.

A Dockerfile is a *post-freeze stretch goal* only — never a blocker.

---

## 4. Branching strategy

Three tiers: **`main`** (stable, demo-ready — protected), **`develop`** (integration — all feature work merges here via PR), and **`feature branches`** (one per pair, short-lived).

```
feature branch  --PR-->  develop  --(build passes)-->  main
```

Rules:

- Branch off **`develop`**, never off `main` or another feature branch.
- Keep PRs small; 1 review + green CI to merge.
- Merge `develop` into your branch before opening a PR, so conflicts surface on your side.
- `main` only ever receives merges from `develop`, once the build is verified.

### Feature branches (one per pair)

| Pair | Branch | Owns |
|---|---|---|
| Generation | `feat/discovery_agent` *(already created)* | Discovery, Script-Gen, prompts, OpenRouter config, README |
| Engine | `feat/engine_core` | Schema, LangGraph graph + repair cycle, Execution node, integration |
| Healing | `feat/healing_loop` | LLM mock, Diagnosis, Repair, human-in-the-loop, the UI |
| Scoreboard | `feat/scoreboard_harness` | Swag Labs baseline, break matrix, HAR replay, harness, metrics |

### Daily Git workflow (per pair)

```bash
# Start (once): get your feature branch
git checkout develop
git pull origin develop
git checkout feat/engine_core          # your pair's branch; or: git checkout -b feat/engine_core

# --- work loop ---
git add <files>                        # or: git add -A
git commit -m "engine: add execution artifact capture"
git push origin feat/engine_core       # first push: git push -u origin feat/engine_core

# Before opening a PR, pull the latest integration branch in:
git fetch origin
git merge origin/develop               # resolve any conflicts locally
git push origin feat/engine_core
```

### Raising a Pull Request (→ develop)

1. Push your branch (above).
2. On GitHub: **New Pull Request**, base = **`develop`**, compare = your feature branch.
3. Title = what changed; link the ticket (e.g. "D3 — Execution artifacts").
4. Request your pair partner as reviewer. CI must be green.
5. Merge after 1 approval. Delete the branch after merge:
   `git push origin --delete feat/engine_core` (recreate later as needed).

### Promoting to `main`

Only the PM does this, after a clean build from `develop`:

```bash
git checkout main
git pull origin main
git merge --no-ff origin/develop
git push origin main
```

---

## 5. Repo layout

```
schemas/        frozen typed contract (B1) — the single hard gate, don't edit without a team call
config/         models.yaml role->model map + model_for() run-mode loader (A2)
graph/          LangGraph graph: nodes, edges, repair cycle (B2)
agents/         discovery, script_gen, diagnosis, repair — one node fn each
tools/          execution (deterministic Playwright) + mock_llm / opencode_llm / claude_llm backends (B3)
ui/             pipeline view + artifact gallery (G1-G3)
harness/        saucedemo runner + metrics (F1-F2) + test_website_cases.py / test_website_runner.py
tests/          unit tests, LLM mocked
fixtures/       HAR recordings + local flow-change fixture (C3, E4)
hello_world/    the two setup smoke scripts
test_website/   local Vite/React clone of Swag Labs with genuine ?break=<mode> DOM changes
main.py         one clear entry point
```

## 6. Ground rules

Temperature 0 everywhere · no `:free` models in the recorded demo · reasoning tier (Sonnet) only for Diagnosis + Repair · schema changes need a team call · `main` always demo-ready · **feature freeze at hour 14 (5am)**.
