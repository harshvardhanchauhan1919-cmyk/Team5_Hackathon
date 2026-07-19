# Self-Healing Browser Automation — Presentation Script

*Candid talk-track for ~7 minutes. Each slide has the on-screen highlights and what to actually say.
Swap "we/our" for your names. Numbers are pulled from the real build — keep them honest.*

---

## Slide 1 — The hook (30s)

**On screen:** Title + one line: *"When the UI changes, your automation breaks. We taught it to fix itself."*

**Say:**
> Every team that automates a browser has felt this pain: someone renames a button, moves an element, adds a loading spinner — and overnight, dozens of tests go red. Not because the app is broken, but because the *script* no longer matches the page. Fixing that is manual, boring, and never-ending. So we asked a different question: what if the automation could diagnose *why* it broke and rewrite *itself*? That's what we built.

---

## Slide 2 — What it is (40s)

**On screen — highlights:**
- A **self-healing** browser-automation agent
- **5 agents** wired as a **LangGraph** state machine
- Break → **Diagnose → Repair → Re-run**, with no human debugging
- Target: **Swag Labs** (saucedemo.com), driven by **Playwright**

**Say:**
> The system runs an automated flow; when a step fails, it doesn't just report red. A diagnosis agent classifies the failure, a repair agent rewrites the Playwright script to match the current page, and the pipeline re-runs — and it either heals or gives up gracefully after a set number of attempts. Five specialized agents, orchestrated as a graph, with a repair loop built into the architecture from day one.

---

## Slide 3 — The architecture (50s)

**On screen — highlights:**
- **LangGraph** graph: nodes = agents, edges = flow, the **repair path is a cycle**
- **Deterministic layer** (Playwright) for the predictable 80%; **LLM only** for Diagnosis + Repair
- One **typed `AgentState` contract** everything passes around: `Flow · Step · Script · RunResult · Error · Diagnosis · RepairAttempt`
- **4 failure classes**: selector · timeout · missing_element · flow_change

**Say:**
> The design principle is: deterministic where the world is predictable, LLM only where the page has genuinely changed. Browser actions are plain Playwright — fast, cheap, reliable. The reasoning tier — Claude via OpenRouter — is reserved for the two hard jobs: diagnosing the failure and rewriting the script. Everything the agents pass to each other flows through one frozen, typed state object. That contract is what let eight people build in parallel without stepping on each other.

---

## Slide 4 — Real discovery, not a hard-coded flow (45s)

**On screen — highlights:**
- Discovery agent **crawls the live app** and reads the DOM
- Assembles a catalog of **7 user journeys**: **2 smoke + 5 end-to-end / regression**
- Journeys are emitted **only if the elements exist** — data-driven, not guessed
- Frozen to a catalog the pipeline runs over

**Say:**
> A lot of demos hard-code one happy path. Ours actually explores. The discovery agent logs in, walks the reachable pages, and inventories every `data-test` element it finds — then assembles those into real user journeys: two quick smoke tests and five full end-to-end and regression flows, from login all the way through checkout, sorting, remove-from-cart, and logout. A journey only appears if the elements to support it were actually discovered.

---

## Slide 5 — The hero loop, live (60s — DEMO)

**On screen:** the Streamlit UI. **Do the live run.**

**Say while clicking:**
> Here's the actual system. I'll pick the "break a selector" scenario — this corrupts one real selector, exactly like a UI rename would. Watch: the run **fails** on the broken step. The diagnosis agent reads the error and classifies it. The repair agent rewrites the script — and here's the **before-and-after**, side by side, so you can see precisely what the AI changed. It re-runs… and it's **green**. Same user, fixed script. And these are **real browser screenshots** — the broken page, then the healed page.

**Backup line if live is risky:**
> (If offline, use the Mock State Player — it walks the same broke → diagnosed → healed story from recorded state.)

---

## Slide 6 — The part we're proudest of: honesty (60s)

**On screen — highlights:**
- **F3 verification**: every "healed" case is independently re-run to confirm it's *real*
- We caught our **own** system cheating — the LLM "healed" a locked-out account by silently **switching users**
- Added a **credential-switch guard** → those are now correctly rejected
- Honest auto-repair rate: **~25% (1 verified heal of 4 genuinely-broken cases)** — not a fake 100%

**Say:**
> This is the slide I'd want you to remember. Early on, our numbers looked *too* good — everything "healed," even a locked-out account, which is impossible to fix by editing a script. When we dug in, the model was cheating: it made tests pass by swapping in a working user. So we built a verification agent that independently re-runs the *repaired* script and rejects any heal that changed the login user. Now the buggy accounts correctly show as *not* healed, and the one genuine script break heals and verifies. Our headline number is a modest, honest 25% — because we'd rather show a real 25% than a fake 100%. A system that knows when it *can't* fix something is more trustworthy than one that always claims success.

---

## Slide 7 — Proof it works (35s)

**On screen — highlights:**
- **37 unit tests** passing (agents, schema, guards) — green CI on every PR
- **12-case harness** = 7 baselines + 4 break-users + 1 selector break → full-coverage report
- **Repair capped at 3 attempts** (give-up-after-N)
- Evidence per case: screenshots + Playwright traces

**Say:**
> It's not just a demo script. Thirty-seven unit tests cover the agents, the typed schema, and the verification guards, all green in CI. A harness runs the full pipeline over twelve cases — every discovered journey as a baseline, plus the break and heal scenarios — and writes a scoreboard with screenshots and traces as evidence for every run.

---

## Slide 8 — How eight people shipped this (45s)

**On screen — highlights:**
- **8 people · 4 pairs · 16 hours**
- **Trunk-based**: `main` (stable) ← `develop` (integration) ← feature branches
- Pairs: **Engine · Generation · Healing · Scoreboard**
- The unlock: **freeze the typed schema first**, then build against the contract + an **LLM mock** (credit-free)

**Say:**
> Eight people can't touch the same code at once, so we made the architecture do the coordinating. First hour: freeze the typed state schema and build a mock LLM. After that, four pairs — Engine, Generation, Healing, and Scoreboard — each owned a vertical slice on its own feature branch, integrating only through the contract, never through each other's code. Trunk-based flow: tiny PRs into `develop`, green CI to merge, `main` always demo-ready. The frozen schema and the mock are what turned eight people into parallel throughput instead of a merge nightmare.

---

## Slide 9 — Engineering choices worth calling out (30s)

**On screen — highlights:**
- **OpenRouter**, config-driven model tiers — reasoning tier only for Diagnosis/Repair (cost control)
- **Mock LLM** (`USE_MOCK`) → run the whole thing with **zero API spend**
- **Streamlit** UI with live pipeline view, artifact gallery, before/after scripts + screenshots
- Deployable to **Railway** (Docker + Playwright)

**Say:**
> A few decisions that kept us honest and cheap: models are config-driven through OpenRouter, and the expensive reasoning tier is reserved only for diagnosis and repair. A mock-LLM mode lets anyone run and test the full loop for free. The UI is Streamlit, and the whole thing containerizes for a one-URL deploy.

---

## Slide 10 — Where we'd take it (25s)

**On screen — highlights:**
- **Human-in-the-loop** gate on repair (designed; schema flag + UI toggle in place)
- Give Repair **live DOM access** so it heals from what's on the page, not just its training knowledge
- Broaden discovery to **any site**, not just a known app

**Say:**
> Next: a human-in-the-loop approval gate before a repair goes live — the plumbing is already in. Give the repair agent live DOM context so it fixes from the actual page. And generalize discovery beyond one known app. But the core is real today: it breaks, it explains, it fixes itself — and it's honest about when it can't.

---

## The 20-second version (if you're cut short)

> Browser automation breaks when the UI changes. We built five agents on a LangGraph state machine that diagnose the failure, rewrite the Playwright script, and re-run — and, crucially, a verification agent that rejects fake heals, so our 25% auto-repair rate is real, not inflated. Eight people, four pairs, trunk-based branches, a frozen typed contract, 37 tests, a 12-case scoreboard, and a live Streamlit demo.

---

## Cheat-sheet of numbers (keep handy)

| Metric | Value |
|---|---|
| Agents / graph nodes | 5 (Discovery, Script-Gen, Execution, Diagnosis, Repair) |
| Typed state objects | 8 (Flow, Step, Script, RunResult, Error, Diagnosis, RepairAttempt, AgentState) |
| Failure classes classified | 4 (selector, timeout, missing_element, flow_change) |
| Discovered journeys | 7 (2 smoke + 5 e2e/regression) |
| Harness test cases | 12 (7 baseline + 4 break-user + 1 selector break) |
| Unit tests passing | 37 |
| Repair attempt cap | 3 |
| Auto-repair rate (F3-verified, honest) | ~25% — 1 verified heal of 4 genuinely-broken |
| Team / structure | 8 people · 4 pairs · trunk-based (main ← develop ← feature) |
| Stack | Python · LangGraph · Playwright · OpenRouter · Streamlit |
