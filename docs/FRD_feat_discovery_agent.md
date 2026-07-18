# Feature Requirement Document — `feat/discovery_agent`

**Branch:** `feat/discovery_agent` · **Pair:** Generation (AI-B + Flex)
**Epics/tickets:** A2 (OpenRouter config), D1 (Flow Discovery), D2 (Script Generator), H1 (README)
**Status:** implemented + verified (crawl → catalog → render, all offline-tested)

---

## 1. What this piece achieves

This branch owns the **front of the pipeline**: it discovers the app's user journeys and turns each into
a **runnable Playwright script**. Everything downstream (Execution → Diagnosis → Repair) runs over the
`Flow`s and `Script`s this branch produces.

Two responsibilities:

1. **Flow Discovery (D1)** — *crawl* the app, find the reachable user journeys, and emit a **catalog** of
   typed `Flow`s tagged smoke / e2e (regression).
2. **Script Generation (D2)** — turn each `Flow` into a Playwright `Script`.

Plus the supporting OpenRouter config (A2).

## 2. How it achieves it — real discovery in two stages

Discovery genuinely explores the site; it is no longer a single hard-coded flow. Both stages are
deterministic and reproducible.

1. **`crawl(page)` — the eyes.** Logs in as `standard_user` and walks the reachable pages (login →
   inventory → cart), reading the DOM to collect every `[data-test]` token. Pure DOM read, no side
   effects beyond navigation. This is what makes discovery *real* — the journeys are built from what is
   actually on the page.
2. **`build_catalog(tokens)` — assembly.** Assembles user journeys from the discovered tokens. A journey
   is emitted **only if the elements it needs were found** (drop the sort control and the sort journey
   disappears). Produces the catalog: **2 smoke + 5 e2e/regression** on Swag Labs.

> An LLM refinement step (renaming/relabelling discovered journeys) was considered but **cut** — as scoped
> it invoked the model and discarded the output, so it added cost without value. Add it back only when it
> demonstrably improves the catalog. Discovery is deterministic today.

**Generate once, freeze.** `generate_catalog(page)` crawls the live site and writes
`fixtures/flow_catalog.json`. The recorded demo runs the pipeline over that frozen catalog, so it never
depends on a live crawl — you can still run the crawl on camera as a "look what it found" beat.

**Script generation stays deterministic template rendering.** Each `Step` → one line of Playwright.
Same `Flow` → identical `Script`, nothing to flake. Action vocabulary is a closed set of 5 verbs.

### The discovered catalog (verified)

| id | type | steps | journey |
|---|---|---|---|
| `smoke_login` | smoke | 5 | login succeeds → inventory shown |
| `smoke_add_to_cart` | smoke | 6 | add one item → cart badge appears |
| `e2e_checkout` | e2e | 13 | login → add → cart → checkout → finish → complete |
| `e2e_multi_item_checkout` | e2e | 14 | add two items → full checkout |
| `e2e_sort_inventory` | e2e | 6 | sort price low→high → inventory still shown |
| `e2e_remove_from_cart` | e2e | 8 | add → open cart → remove → cart usable |
| `e2e_logout` | e2e | 7 | menu → logout → back at login |

### Data flow

```
generate_catalog(page) ──> fixtures/flow_catalog.json   (offline, once; the frozen catalog)

discovery_node(state, config) ─ picks flow by id + injects user/url ─> state.flow : Flow
                                                                            │
script_gen_node(state) ──> state.script : Script   # Script.code is a Python module string
                                                                            │
                                                          (handed to Execution / D3, Engine)
```

Category is carried by the **flow-id convention** (`smoke_*` / `e2e_*`) — no schema change. The "break"
is injected by passing a different `user` in config; `_inject` swaps the login value in the selected flow.

### The Script contract (interface with Execution, D3)

`Script.code` is a Python module string defining exactly one function:

```python
def run(page):
    page.goto('https://www.saucedemo.com/', timeout=60000)
    page.fill('[data-test="username"]', 'standard_user')
    ...
    page.wait_for_selector('[data-test="complete-header"]', timeout=60000)
```

The Execution node execs the code and calls `run(page)` with a live Playwright page. Any exception raised
inside `run` is exactly what Diagnosis later classifies. **This tiny contract is the integration seam
between this branch and Engine — agree on it, then both build independently.**

### How we use LangGraph (team-wide clarification)

LangGraph is our **orchestrator**, not an agent-authoring library. Decision (locked): we use
**LangGraph as orchestrator with plain-function nodes** (not the prebuilt `create_react_agent`).

- The only file that imports `langgraph` is `graph/build.py` — it builds the `StateGraph`, wires the
  nodes, and defines the edges + repair cycle. That is where "the agent system" lives.
- Every node — including Discovery and Script-Gen here — is a plain `def node(state) -> state` function.
  Nodes do **not** import langgraph; that is idiomatic, not a gap.
- Deterministic nodes (Discovery, Script-Gen, Execution) contain no LLM. Reasoning nodes (Diagnosis,
  Repair) call the LLM *inside* the function via `config.model_for()` (LangChain `ChatOpenAI`).
- **Human-in-the-loop does not apply to Discovery or Script-Gen.** The HITL gate (LangGraph
  checkpointer + `interrupt()`) sits only on the Repair → re-run edge, added later by the Healing pair.

### State, input, and wiring — how the three concerns are handled

**Nodes, edges, state passing (this is genuine LangGraph, not manual chaining).** The two agents are
nodes wired in `graph/build.py`:

```python
g.add_node("discovery", discovery_node)
g.add_node("script_gen", script_gen_node)
g.add_edge("discovery", "script_gen")   # node 1's output feeds node 2 via shared state
```

Nodes return a **partial state update** (e.g. `{"flow": ...}`); LangGraph merges it into `AgentState`.
Discovery writes `flow`; the edge advances; Script-Gen reads `state.flow` and writes `script`. The
"output of agent 1 is the input to agent 2" contract is the shared state, not a direct return value.

**State preservation from the start.** One `AgentState` is created at invoke and threaded through every
node, accumulating `flow → script → …`. To *persist* it across steps (and survive the later HITL
interrupt/resume), the graph is compiled with a checkpointer and invoked with a `thread_id`:

```python
app = g.compile(checkpointer=MemorySaver())
app.invoke(AgentState(), config={"configurable": {"thread_id": "run-1", ...}})
```

**Input as a parameter (not hard-coded).** Per-run input arrives via `config["configurable"]`, so the
target URL, user, and flow id are passed in — never baked into the code or the frozen schema:

```python
app.invoke(AgentState(), config={"configurable": {
    "thread_id": "run-1",
    "target_url": "https://www.saucedemo.com/",
    "user": "standard_user",   # switch to "problem_user" to inject the break
    "flow_id": "e2e_checkout",  # any id from the discovered catalog
}})
```

`discovery_node(state, config)` reads these (all optional, defaulting to the Swag Labs happy path).

> **Ownership note:** the two enablers above — the **checkpointer** (compile) and passing **config** at
> **invoke** — live in `graph/build.py` and `main.py`, which are **Engine-owned**. This branch's nodes are
> already config-aware and return partial updates, so they work with the current graph *without* changes
> (config is optional). The exact Engine snippet is in `CHANGESET_feat_discovery_agent.md`.
> *(Note for Engine: LangGraph 1.2.x warns when checkpointing unregistered Pydantic types — register the
> `schemas` module in `allowed_msgpack_modules` when wiring the real checkpointer.)*

### Action vocabulary (Step.action → Playwright)

| `Step.action` | Renders to |
|---|---|
| `goto` | `page.goto(value, timeout=60000)` |
| `fill` | `page.fill(selector, value)` |
| `click` | `page.click(selector)` |
| `select` | `page.select_option(selector, value)` |
| `expect_visible` | `page.wait_for_selector(selector, timeout=60000)` |

Any other action raises `ValueError` at generation time (fail fast, not at runtime).

## 3. Scope

**In scope**
- Real discovery: `crawl(page)` reads the live DOM, `build_catalog(tokens)` assembles journeys from what
  was found — **2 smoke + 5 e2e/regression** — frozen to `fixtures/flow_catalog.json`.
- Per-run selection + input via LangGraph `config` (`flow_id`, `user`, `target_url`); user switch drives
  break injection via `_inject`.
- Deterministic `Flow` → Playwright `Script` rendering with a 5-verb action vocabulary.
- Nodes return partial state updates, config-aware, ready to wire into the graph.
- Unit tests for crawl, catalog assembly, rendering, selection, break injection (no live browser/LLM).

**Out of scope (explicitly)**
- Generic journey synthesis for arbitrary sites — journey *shapes* are Swag-Labs-aware; the crawl decides
  which apply and with which discovered selectors.
- Any LLM in these agents — discovery is deterministic (crawl + assembly). **D4 (stable system prompts) is
  N/A**; `agents/prompts.py`, the old LLM fallback, and the no-op `refine_with_llm` were removed as dead
  code. Diagnosis/Repair prompts live on the Healing branch. Reallocate the D4 effort.
- Running the browser during the pipeline — that's the Execution node (D3, Engine). We only *generate*.
- Compiling the checkpointer / passing config at invoke — Engine-owned (`build.py`, `main.py`).
- Diagnosis/Repair, the break-user matrix, the UI, the harness — other branches.

**Assumptions / dependencies**
- The frozen schema (`schemas/__init__.py`, B1) is available — this branch imports `Flow/Step/Script/AgentState`.
- `langchain-core` is installed (for the `RunnableConfig` type) — already in `requirements.txt`.
- Swag Labs selectors are the stable `[data-test="..."]` set; Scoreboard (C1) confirms them empirically.

## 4. Acceptance criteria

- `crawl(page)` returns the discovered `[data-test]` token set (login + add-to-cart present).
- `build_catalog(tokens)` yields exactly **2 smoke + 5 e2e** flows on the Swag Labs token set.
- A journey is omitted when its required elements are absent (drop `product-sort-container` → no
  `e2e_sort_inventory`).
- Every catalog flow renders to valid Python defining a callable `run`, and executes against a fake page.
- `discover_flow(flow_id)` selects by id; unknown id raises `KeyError`; unknown action raises `ValueError`.
- `discover_flow(flow_id, user="problem_user")` swaps the login username (break injection).
- `discovery_node(state, config)` reads `config["configurable"]` and returns `{"flow": ...}`;
  `script_gen_node(state)` returns `{"script": ...}` and raises `ValueError` if `flow` is missing.
- All unit tests green with no live browser and no LLM.

*(All criteria verified in the sandbox: crawl→catalog produced 2 smoke + 5 e2e, all 7 rendered to valid
Playwright and executed against a fake page, break injection and config-driven selection confirmed, and the
graph wiring — discovery→script_gen edge, config input, partial-update state, `MemorySaver` — checked
against a real LangGraph 1.2.9 `StateGraph`.)*
