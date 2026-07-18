# Testing Guide — Self-Healing Loop (`feat/healing_loop`)

This guide provides instructions on how to verify and test the current self-healing pipeline implementation on the `feat/healing_loop` branch. Testing covers both automated unit tests (using mocked LLM outputs) and manual visualization (using the Streamlit dashboard).

---

## 1. Prerequisites

Before running any tests, make sure you have installed the required dependencies:

```bash
# Install package dependencies
pip install -r requirements.txt

# Ensure Playwright browser binaries are present
playwright install chromium
```

---

## 2. Automated Testing (Pytest)

We use `pytest` for automated, offline, and CI-safe testing. All network calls to OpenRouter are mocked, so no API keys or internet connections are required.

### Run All Tests
Execute the following command at the repository root:
```bash
pytest tests/
```

Expected output:
```
collected 14 items

tests\test_diagnosis_node.py .....                                       [ 35%]
tests\test_repair_node.py ....                                           [ 64%]
tests\test_skeleton.py .                                                 [ 71%]
tests\test_verify.py ....                                                [100%]

============================= 14 passed in 0.88s ==============================
```

### Run Specific Test Files
> [!NOTE]
> These unit tests are **not GUI tests**. They run completely offline, headless, and without launching browsers, using mocked outputs to test the core logic of each agent node and verification hook.

If you are modifying a specific component, you can isolate tests like so:

- **Diagnosis Node tests** (`tests/test_diagnosis_node.py`):
  ```bash
  pytest tests/test_diagnosis_node.py -v
  ```
  * `test_diagnosis_node_success`: Validates parsing of standard mock selector error details into a structured `Diagnosis` object.
  * `test_diagnosis_node_fallback_on_invalid_json`: Verifies that malformed JSON responses from the LLM are handled gracefully with a safe fallback instead of throwing exceptions.
  * `test_diagnosis_node_strips_markdown_fences`: Confirms that JSON outputs returned inside markdown code fences (e.g. ` ```json ... ``` `) are stripped before parsing.
  * `test_diagnosis_node_all_error_kinds`: Validates that all 4 error kinds (`selector`, `timeout`, `missing_element`, `flow_change`) map correctly to their respective mock responses.
  * `test_diagnosis_node_missing_logs_and_screenshots`: Confirms that missing log content or screenshot files do not cause crashes.

- **Repair Node tests** (`tests/test_repair_node.py`):
  ```bash
  pytest tests/test_repair_node.py -v
  ```
  * `test_repair_node_success`: Verifies that the repaired script updates state and appends to the `RepairAttempt` history.
  * `test_repair_node_strips_code_fences`: Checks that python code wrapped in markdown code fences is cleaned before writing the script.
  * `test_repair_node_exception_handling`: Verifies that connection/model exceptions during invocation are caught, logged, and appended as safe comment annotations in the script without crashing the loop.
  * `test_repair_node_history_formatting`: Validates historical attempt logs rendering and character limitation truncation.

- **Verification Hook tests** (`tests/test_verify.py`):
  ```bash
  pytest tests/test_verify.py -v
  ```
  * `test_verify_healed_success`: Asserts that a run result status of `"pass"` without errors validates as `True`.
  * `test_verify_healed_failed_status`: Checks that a run result status of `"fail"` returns `False`.
  * `test_verify_healed_with_error`: Verifies that status `"pass"` containing hidden errors returns `False`.
  * `test_verify_healed_with_original_context`: Confirms verification passes when comparing a successful re-run against the original failure details.

- **Skeleton Pipeline tests** (`tests/test_skeleton.py`):
  ```bash
  pytest tests/test_skeleton.py -v
  ```
  * `test_pipeline_runs_end_to_end`: Assures the entire compiled LangGraph runs end-to-end through the graph nodes without raising exceptions.

---

## 3. Manual Verification & Demo (Streamlit UI)

To visually verify the healing loops, screenshots, and pipeline state transitions, launch the interactive dashboard:

```bash
streamlit run ui/app.py
```

Streamlit will boot a local web server (usually at `http://localhost:8501`). Open this address in your web browser.

### Streamlit UI Dashboard Layout & Elements

When the dashboard launches, you will see a dark-themed, glassmorphic layout divided into the following panels:

1. **Sidebar Controller & Config**:
   - **Operation Mode**: 
     * *Mock State Player (Demo)*: An offline player loading static state snapshots. Useful for visual walk-throughs, UI development, and demo presentations without consuming API credits or running live browsers.
     * *Live Graph Execution*: Compiles the real LangGraph graph using the state schema and executes the self-healing agent pipeline on a live environment (uses mock LLM if `USE_MOCK=1`).
   - **HITL Checkbox (Human-in-the-Loop)**: Pause execution before re-running a repaired script. When checked, the graph triggers an `interrupt()` between the `Repair` and `Execution (Re-run)` nodes, displaying the proposed code modifications and waiting for a manual click on "Proceed".
   - **Max Healing Attempts**: Limits loop iterations (1–5 attempts). If a repaired script fails again, the agent will retry healing up to this limit before halting to prevent infinite execution loops.
   - **State Player Controls**: (Visible in Mock Mode only) Selection buttons representing stages `1` to `4` of the healing loop.
   - **Live Runner Controls**: (Visible in Live Mode only) Trigger button for the graph.

2. **Main Page Header**: Displays titles showing you are running the `feat/healing_loop` branch.

3. **G1 — Live Agent Pipeline View**:
   - A horizontal node flow tracing: `Discovery 🔍` → `Script Gen 📝` → `Execution 🚀` → `Diagnosis 🩺` → `Repair 🔧`.
   - Each node displays its status dynamically:
     - `pending` (opaque gray) — Node has not been reached.
     - `active` (glowing blue border) — Node is executing or current.
     - `pass` (glowing green border) — Node completed successfully.
     - `fail` (glowing red border) — Node execution failed and triggered the repair loop.
   - The connector lines between completed nodes turn green.

4. **G2 — Artifact Gallery & Details**:
   - **Execution Failure Card**: (Appears only on failure) A red-accented panel presenting the active `ErrorKind`, `Error Message`, and failing step number.
   - **Diagnosis Report Card**: (Appears only on failure) A blue-accented panel outlining the classified root cause, suggested fix instructions, and model confidence percentages.
   - **Script Code View**: Tabs to toggle between:
     - *Original / Current Script*: Displays the syntax-highlighted Playwright script.
     - *Repaired Script History*: Shows code versions produced by previous repair attempts.
   - **Screenshots & Logs**: Tabs to view:
     - *Screenshots*: Side-by-side snapshots captured during executions (original failing vs repaired success runs).
     - *Execution Logs*: Plain-text log streams from both the original run and all repair attempts.

---

### Step-by-Step Manual Walkthrough

Follow these steps to observe the pipeline's self-healing UI transitions:

#### Option A: Mock State Player (Offline Walkthrough)
1. Select **Operation Mode** → `Mock State Player (Demo)`.
2. Select **Select Execution Stage** → `1. Initial Discovery (Pending)`:
   - **What it demonstrates**: *Happy Path Startup*. The Discovery agent has mapped the flow sequence and the Script Gen agent has written the initial Playwright script. The script is now actively executing.
   - **Observe**: The `Discovery` and `Script Gen` nodes are green (`pass`). The `Execution` node is blue (`active`), and subsequent nodes are grayed out. The code view shows the script currently running.
3. Select `2. First Run Failed (Error Detected)`:
   - **What it demonstrates**: *Crash & Active Diagnosis*. The Playwright script failed (e.g. at step 7 click action). The pipeline immediately routes the failure to the Error Diagnosis agent, which is currently running in the background.
   - **Observe**: The `Execution` node turns red (`fail`). The `Diagnosis` node glows blue (`active`). Because diagnosis is actively running, the report below displays `Diagnosis pending...`, and the execution log shows the locator timeout crash traceback.
4. Select `3. Error Diagnosed (Root Cause Found)`:
   - **What it demonstrates**: *Diagnosis Completion*. The Error Diagnosis agent finished analysis, classified the error kind (`selector`), and recommended the fix.
   - **Observe**: The `Diagnosis` node turns green (`pass`). The **Diagnosis Report** card renders, detailing the root cause (renamed selector) and recommending swapping `checkout-btn-renamed` with `checkout` (confidence: 95%).
5. Select `4. Script Healed (Re-run Passed)`:
   - **What it demonstrates**: *Self-Repair & Re-run Verification*. The Adaptive Repair agent modified the script. The script was re-run, passed successfully, and was validated by the verification hook.
   - **Observe**: The `Repair` node and `Execution` node both glow green (`pass`). The **Repaired Script History** contains Attempt 1 code showing the selector update. Under **Screenshots**, you see the successful checkout completed snapshot.

#### Option B: Live Graph Execution
1. Set the environment variable `USE_MOCK=1` in your console before launching Streamlit.
2. Select **Operation Mode** → `Live Graph Execution`.
3. Configure **Max Healing Attempts** (e.g. `3`).
4. Click the **Run Live Pipeline** button.
5. *Observe*: The pipeline completes immediately showing green (`pass`) up to the `Execution` node.
   
> [!IMPORTANT]
   > **Why does the Live execution finish immediately and skip the healing loop?**
   > - The **Script Generator** (Generation pair) and the **Execution Node** (Engine pair) are developed on other branches and are currently **stubs** on this branch.
   > - The script gen stub outputs a dummy code line (`# generated Playwright script goes here`).
   > - The execution stub (`tools/execution.py`) returns a successful status (`RunResult(status="pass")`) without actually launching a browser.
   > - Because execution is reported to succeed, the LangGraph graph conditional edge transitions directly to the `END` node, bypassing the healing nodes (`Diagnosis` and `Repair`) since there is no error to heal.
   > - At the **9 PM convergence phase**, once all branches are merged, the live execution node will run the real browser automation, hit actual Swag Labs failures, and trigger our self-healing agents in real-time.

> [!NOTE]
   > **Understanding `USE_MOCK` in Live Execution Mode:**
   > - **With `USE_MOCK=1` (Mock Mode)**: The Live Runner uses `FakeModel` instead of calling OpenRouter. 
   >   * *Limitation*: The mock model yields static, hardcoded responses (`_DIAGNOSIS_CANNED` for diagnosis and `_REPAIR_CANNED` for repair). It is excellent for verifying graph wiring, state flow, and UI rendering without API usage, but it cannot dynamically repair new or dynamic script errors.
   > - **With `USE_MOCK=0` or Unset (Real Mode)**: The Live Runner will attempt to call OpenRouter models (e.g. Claude Sonnet).
   >   * *Requirement*: Requires a valid `OPENROUTER_API_KEY` defined in a `.env` file at the root of the repository.
   >   * *Behavior*: Will perform dynamic, reasoning-tier diagnoses and script repairs (though again, on this branch, you will need to manually mock execution failure state to force the graph into the repair branch).

---

### Use Cases for Demonstration

When demonstrating or manually testing the UI, observe the transitions corresponding to these two main scenarios:

#### Use Case 1: Selector Update (Renamed Checkout Selector)
* **Setup**: A frontend update shifts the Swag Labs Checkout button's `data-test` attribute from a deprecated `checkout-btn-renamed` tag to the standard `checkout` tag. The original Playwright script tries to locate the old tag and hangs.
* **Flow to Observe**:
  1. **Stage 1 (Discovery & Generation)**: Pipeline starts green. The script containing the old selector `checkout-btn-renamed` is created.
  2. **Stage 2 (Run Failed)**: Execution fails. Under **Screenshots & Logs**, observe the red card warning: `Timeout 5000ms exceeded waiting for selector [data-test='checkout-btn-renamed']`.
  3. **Stage 3 (Diagnosed)**: Under the **Diagnosis Report** column, observe:
     - **Root Cause**: Explanation stating the checkout selector is no longer present.
     - **Suggested Fix**: Recommendation to swap `[data-test='checkout-btn-renamed']` with `[data-test='checkout']`.
  4. **Stage 4 (Healed)**: Click the **Repaired Script History** tab. Observe that the script has swapped the target button call. The final node glows green, and the success screenshot (`screenshot_success.png`) is captured.

#### Use Case 2: Timeout Adjustment (Server Delay)
* **Setup**: High network congestion or database loading delays cause page elements to load slower than standard browser thresholds, triggering a timeout failure.
* **Flow to Observe**:
  1. **Stage 2 (Run Failed)**: The script crashes on page load, yielding a `timeout` kind error.
  2. **Stage 3 (Diagnosed)**: The Diagnosis agent suggests adding an explicit wait statement (`networkidle`) and raising target timeouts.
  3. **Stage 4 (Healed)**: The script is rewritten to contain:
     ```python
     page.wait_for_load_state("networkidle")
     # Wait with increased timeout limit (10000ms)
     ```
     The verification re-run succeeds.

---

## 4. Terminal-based Manual Observer (CLI Simulation)

If you prefer terminal output to inspect the data structures in real-time, you can execute the mock simulation script:

```bash
python tools/test_observer.py
```

This script manually injects a simulated Playwright failure state, executes the `diagnosis_node` and `repair_node`, prints the formatted JSON diagnosis reports, outputs the syntax-highlighted repaired Python script, and finally runs the validation check through the `verify_healed` hook.

---

## 5. Troubleshooting

- **Error: `ModuleNotFoundError`**: Ensure your current working directory is the root of the repository and that you have activated your virtual environment.
- **API Key Prompts**: If the application prompts you for an `OPENROUTER_API_KEY`, ensure `USE_MOCK=1` is exported/set in your environment so that the system falls back to the local offline mock.
