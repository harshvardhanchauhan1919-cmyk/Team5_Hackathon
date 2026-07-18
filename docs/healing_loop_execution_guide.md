# Healing Loop Execution Guide for engine_core

This guide documents how the engine_core healing loop executes after an initial execution failure. It is intended to complement the execution guide and describe the end-to-end behavior of diagnosis, repair, and re-execution.

## Purpose

The healing loop is the retry path in the engine_core workflow:

1. Discovery produces a flow.
2. Script generation produces a runnable script.
3. Execution runs the generated script.
4. If execution fails, Diagnosis inspects the failure.
5. Repair generates a revised script.
6. Execution runs the repaired script again.
7. The loop continues until the run passes or the maximum attempt limit is reached.

## Contract

The healing loop relies on the shared state contract in the schemas:

- `state.flow` contains the discovered workflow.
- `state.script` contains the generated executable script.
- `state.result` contains the latest execution outcome.
- `state.diagnosis` contains the structured diagnosis from the failure.
- `state.repair_attempts` stores the history of repair attempts.
- `state.max_attempts` caps the retry loop.

The key requirement is that each node must preserve and update the shared state rather than passing data directly between nodes.

## Execution flow

### 1. Initial execution

The graph begins with discovery, then script generation, then execution.

- `discovery` selects or builds a flow.
- `script_gen` turns the flow into `state.script.code`.
- `execution` executes the generated script against a live Playwright page.

If execution succeeds, the graph exits with a passing result.

### 2. Failure handoff

If execution fails, the execution node must:

- return a `RunResult` in `state.result`
- leave the error data in `state.result.error`
- preserve the script and flow context for downstream diagnosis

This ensures the failure becomes structured data rather than an uncaught exception.

### 3. Diagnosis

The diagnosis node should inspect the failure and produce a `Diagnosis` object containing:

- the original `Error`
- a root cause summary
- a confidence score
- a suggested fix

The diagnosis should explain why the script failed and what kind of repair is needed.

### 4. Repair

The repair node uses the diagnosis to produce a revised script.

Expected behavior:

- it should create a new `Script` object
- it should update `state.script` with the repaired script
- it should append a `RepairAttempt` entry to `state.repair_attempts`
- it should preserve the previous result for traceability

### 5. Re-execution

After repair, the graph returns to the execution node.

The second execution attempt should:

- run the repaired script from `state.script.code`
- reuse the same flow context
- capture fresh artifacts for the retry
- update `state.result` again

## Error handling expectations

The healing loop should never let the execution node crash the whole graph without producing a result. Instead, it should always return a structured failure in `state.result`.

Typical error categories:

- `missing_element` for selectors that do not resolve
- `timeout` for waiting or action timeouts
- `selector` for general locator issues
- `flow_change` for unexpected execution path issues

## Suggested implementation pattern

```python
# execution node contract
state.result = RunResult(
    script_id=state.script.flow_id,
    status="fail",
    logs=str(exc),
    screenshots=[...],
    trace=[...],
    error=Error(kind="missing_element", message=str(exc), step_index=0),
)
```

```python
# diagnosis node contract
state.diagnosis = Diagnosis(
    error=state.result.error,
    root_cause="The target element was not found",
    confidence=0.95,
    suggested_fix="Update the selector or wait for the element to appear",
)
```

```python
# repair node contract
state.repair_attempts.append(
    RepairAttempt(
        diagnosis=state.diagnosis,
        new_script=Script(flow_id=state.flow.id, code=new_script_code),
        attempt_no=len(state.repair_attempts) + 1,
    )
)
state.script = state.repair_attempts[-1].new_script
```

## Loop termination

The healing loop should stop when one of the following happens:

- execution passes
- the maximum repair attempts are reached
- the graph reaches a terminal state with a final failure

A typical guard is:

- `state.max_attempts = 3`
- stop retrying after the current attempt count exceeds that limit

## Practical testing checklist

To validate the healing loop end to end:

1. Start from a known failing flow.
2. Confirm execution produces a structured failure.
3. Confirm diagnosis captures the root cause.
4. Confirm repair produces a revised script.
5. Confirm the next execution attempt uses the repaired script.
6. Confirm the graph terminates cleanly after success or max attempts.

## Notes

This guide focuses on the behavior of the healing loop and should be used alongside the execution guide when implementing or debugging engine_core.
