# Handover → Engine pair: consuming the generated script in Execution (D3)

How the Execution node consumes what Discovery + Script-Gen produce. This is the seam between
`feat/discovery_agent` (done) and `feat/engine_core` (you).

## The contract (already frozen — build to this)

- The script arrives on the shared state as **`state.script`** (a `Script` object).
- **`state.script.code`** is a Python module string that defines exactly one function: `def run(page): ...`.
- **`state.script.flow_id`** tells you which discovered flow it came from (use it in logs / artifact names).
- You get `state.script` because the graph runs `script_gen → execution`; the edge carries control, the
  state carries the data. Don't pass anything between nodes directly.

## What Execution must do

- Read `state.script.code` — do **not** re-generate it; Script-Gen already produced it.
- `exec` the code to define `run`, then call `run(page)` against a **live Playwright page**.
- Wrap the run in try/except: a clean finish → success; any exception → that's the failure Diagnosis reads.
- Capture artifacts during/after the run: screenshots, video, trace, logs.
- Write your output back to state as **`state.result`** (a `RunResult`) — that's what flows onward.

## Minimal reference implementation

```python
from playwright.sync_api import sync_playwright
from schemas import AgentState, RunResult, Error

def execution_node(state: AgentState) -> dict:
    script = state.script                     # <-- input from Script-Gen
    ns: dict = {}
    exec(compile(script.code, "<generated>", "exec"), ns)   # defines run(page)
    with sync_playwright() as p:
        page = p.chromium.launch().new_page()
        try:
            ns["run"](page)                   # execute the generated flow
            result = RunResult(script_id=script.flow_id, status="pass",
                               screenshots=[...], video=..., trace=...)
        except Exception as e:
            result = RunResult(script_id=script.flow_id, status="fail",
                               error=Error(kind="selector", message=str(e)),
                               screenshots=[...])
        finally:
            page.context.browser.close()
    return {"result": result}                 # <-- output onward to Diagnosis
```

## Error classification (rough — Diagnosis refines it)

- Playwright `TimeoutError` on an action → `Error.kind="timeout"`.
- Selector not found / element missing → `"selector"` or `"missing_element"`.
- Wrong page / step out of order → `"flow_change"`.
- Set `Error.step_index` if you can map the exception to a step (helps Diagnosis + the UI).

## Do / don't

- **Do** treat `state.script.code` as the source of truth; run it as-is.
- **Do** always return a `RunResult` (even on failure) — never let the node raise; the failure is data.
- **Do** capture artifacts even on failure — the UI shows before/after-repair screenshots.
- **Don't** import from `agents/` — Execution only needs `schemas`. Keeps the layers clean.
- **Don't** edit `schemas/__init__.py` (frozen) or `agents/*` (Generation's). Your files: `tools/execution.py`, `graph/build.py`, `main.py`.

## Wiring reminders (your files)

- `graph/build.py`: `g.add_edge("script_gen", "execution")` already exists; keep it.
- To persist state / enable HITL later: `g.compile(checkpointer=MemorySaver())` and pass a `thread_id`
  in `main.py`'s invoke config (snippet in `CHANGESET_feat_discovery_agent.md`).
- Optional demo nicety: write `state.script.code` to an artifacts `.py` so judges can see the script
  before vs after repair.

## How to try it against a real discovered flow

```python
from agents.discovery import discover_flow
from agents.script_gen import render_script
flow = discover_flow("e2e_checkout")     # or smoke_login, e2e_logout, ...
print(render_script(flow))               # this string is exactly state.script.code
```
