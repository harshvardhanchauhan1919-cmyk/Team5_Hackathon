# Team5 — Self-Healing Browser Automation Agent

When a browser automation run fails, the system diagnoses *why*, rewrites its own Playwright script (adapting to changed flows), and re-runs — no human debugging. Built on **LangGraph** + **Playwright**, models via **OpenRouter**. Target site: **Swag Labs** (saucedemo.com).

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
#   then paste the shared OPENROUTER_API_KEY into .env

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

## 2. Do we need Docker? No.

**We run everything locally — no Docker image.** Playwright ships its own browser binaries via `playwright install chromium`, so there's nothing to containerize for the demo. Docker was in the original PRD only to bundle a self-built demo site; since we target the live Swag Labs site, that reason is gone.

- **Local run:** the setup above is the whole story. `python main.py` runs the pipeline.
- **MCP:** not needed for testing. We drive the browser directly through Playwright's own API (deterministic and fast); an MCP browser server would add a moving part we don't need under the time crunch.
- **Determinism for CI + the recorded demo:** instead of Docker, we record a **HAR/trace** of Swag Labs (ticket C3) and replay it, so runs don't depend on the live network.

A Dockerfile is a *post-freeze stretch goal* only — never a blocker.

---

## 3. Branching strategy

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

## 4. Repo layout

```
schemas/      frozen typed contract (B1) — the single hard gate, don't edit without a team call
config/       models.yaml role->model map + model_for() loader (A2)
graph/        LangGraph graph: nodes, edges, repair cycle (B2)
agents/       discovery, script_gen, diagnosis, repair — one node fn each
tools/        execution (deterministic Playwright) + mock_llm (B3)
ui/           pipeline view + artifact gallery (G1-G3)
harness/      scoreboard runner + metrics (F1-F2)
tests/        unit tests, LLM mocked
fixtures/     HAR recordings + local flow-change fixture (C3, E4)
hello_world/  the two setup smoke scripts
main.py       one clear entry point
```

## 5. Ground rules

Temperature 0 everywhere · no `:free` models in the recorded demo · reasoning tier (Sonnet) only for Diagnosis + Repair · schema changes need a team call · `main` always demo-ready · **feature freeze at hour 14 (5am)**.
