# Change set — `feat/discovery_agent`

Files created / modified on this branch. Only files in this list belong to the Generation pair.
**Do not edit `schemas/__init__.py`** — it's the frozen contract (Engine-owned).

## New files

| File | Purpose | Ticket |
|---|---|---|
| `fixtures/flow_catalog.json` | The **frozen discovered catalog** — 2 smoke + 5 e2e flows, produced by `generate_catalog`. Consumed at runtime and by the harness. | D1 |
| `tests/test_discovery.py` | Unit tests: crawl, catalog assembly (2 smoke + 5 e2e), conditional omission, selection, break injection, config. | D1 |
| `tests/test_script_gen.py` | Unit tests: valid Python, ordered Playwright calls, the `select` action, guards. | D2 |
| `docs/FRD_feat_discovery_agent.md` | Feature requirement document. | — |
| `docs/CHANGESET_feat_discovery_agent.md` | This file. | — |

## Modified files (stub → real implementation)

| File | After | Ticket |
|---|---|---|
| `agents/discovery.py` | Real discovery: `crawl(page)` (DOM inventory) → `build_catalog(tokens)` (2 smoke + 5 e2e, journeys emitted only if elements found) → `generate_catalog` freezes to JSON. Runtime: `load_catalog`, `discover_flow(flow_id, user, url)` with `_inject` break injection, `discovery_node(state, config)` → `{"flow": ...}`. | D1 |
| `agents/script_gen.py` | Deterministic `render_script(flow)` (Step→Playwright, **5-verb** vocab incl. `select`); `script_gen_node(state)` → `{"script": ...}`. | D2 |

## Producer → consumer handoff (flag for Scoreboard)
`fixtures/flow_catalog.json` is **produced** by this branch (`generate_catalog`) and **consumed** by the
Scoreboard harness (F1) as its `{flow × break}` matrix. `fixtures/` is Scoreboard's directory — this is a
new data artifact, not an edit to their code, but worth a heads-up at the sync so the harness reads this path.
To regenerate live: `generate_catalog(page, model=optional)` against saucedemo.com.

## Removed files (dead code — deterministic decision)

| File / symbol | Why removed |
|---|---|
| `agents/prompts.py` | D4 system prompts are unused once Discovery/Script-Gen are LLM-free. **D4 is N/A on this branch** — reallocate that effort. Diagnosis/Repair prompts live on the Healing branch. |
| `generate_with_llm()` (was in `script_gen.py`) | LLM flow-authoring path; not on the demo path and unreachable — removed to keep the branch dead-code-free. |
| `refine_with_llm()` (was in `discovery.py`) | LLM re-labelling step that invoked the model and discarded the output — a no-op. Cut per ponytail-review (~12 lines). |

## Files this branch depends on but does NOT modify

| File | Why | Owner |
|---|---|---|
| `schemas/__init__.py` | Import `Flow`, `Step`, `Script`, `AgentState`. Frozen — never edit. | Engine |
| `graph/build.py` | Adds our two nodes + the edge. Needs the checkpointer (below). | Engine |
| `main.py` | Passes `config` (URL/user/flow) at invoke. | Engine |

## Node contract (how these plug into the graph)
- Nodes return **partial state updates** (`{"flow": ...}`, `{"script": ...}`); LangGraph merges into `AgentState`.
- `discovery_node(state, config)` — config-aware; input is optional and defaults to the Swag Labs happy path.
- `script_gen_node(state)` — reads `state.flow`, writes `state.script`.
- **Backward-compatible:** because config is optional, these work with the *current* `build.py`/`main.py`
  unchanged. The snippet below is only needed to (a) pass real input and (b) persist state for HITL.

## Handoff to Engine — the only two lines they need (their files, not ours)

`graph/build.py` — compile with a checkpointer so state persists across steps / survives HITL:
```python
from langgraph.checkpoint.memory import MemorySaver
app = g.compile(checkpointer=MemorySaver())
```

`main.py` — pass per-run input + a thread id at invoke:
```python
config = {"configurable": {
    "thread_id": "run-1",
    "target_url": "https://www.saucedemo.com/",
    "user": "standard_user",   # switch to inject the break
    "flow_id": "swaglabs_checkout",
}}
final = app.invoke(AgentState(), config=config)
```
> LangGraph 1.2.x warns when checkpointing unregistered Pydantic types; register the `schemas` module in
> `allowed_msgpack_modules` when wiring the real checkpointer.

## Suggested commit sequence
1. `gen: crawl + catalog discovery, 2 smoke + 5 e2e (D1)` — `agents/discovery.py`, `fixtures/flow_catalog.json`, `tests/test_discovery.py`
2. `gen: Playwright script renderer + select action (D2)` — `agents/script_gen.py`, `tests/test_script_gen.py`
3. `gen: remove unused D4 prompts + LLM path (dead code)` — delete `agents/prompts.py`
4. `docs: FRD + change set` — the two docs

Then open a PR into `develop`.
