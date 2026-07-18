# PRD — Self-Healing Loop Feature (`feat/healing_loop`)

This document describes the completed features, components, and integration specifications for the **Self-Healing Loop** built on the `feat/healing_loop` branch. It serves as the source of truth for team members and AI agents collaborating on the project, detailing how the healing components function and how they merge into `develop`.

---

## 1. Overview & Purpose

The purpose of the `feat/healing_loop` branch is to implement the core "healing loop" capability:
1. **Diagnosis**: Understand why a Playwright script run failed.
2. **Repair**: Generate a corrected version of the script using reasoning LLMs.
3. **Re-Run**: Execute the script again (controlled by the Engine's graph build).
4. **Verification**: Verify that the healed run passed without side effects.
5. **Visualization**: Provide a premium Streamlit dashboard to view run logs, screenshots, and live pipeline step transitions.

---

## 2. Completed Scope & Epics

| Epic / Ticket | Component | Description | Location |
|:---|:---|:---|:---|
| **B3 (Mock LLM)** | `FakeModel` | A deterministic, offline, role-aware model mock supporting JSON outputs and code generation. | [mock_llm.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/tools/mock_llm.py) |
| **E1 (Diagnosis)** | `diagnosis_node` | Error Diagnosis node analyzing failed runs and classifying error classes. | [diagnosis.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/agents/diagnosis.py) |
| **E2 (Repair)** | `repair_node` | Adaptive Repair node that modifies Playwright scripts based on diagnosis reports. | [repair.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/agents/repair.py) |
| **E3 (Prompts)** | System Prompts | Stable few-shot prompts defining error taxonomy and repair rules. | [diagnosis_prompt.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/agents/diagnosis_prompt.py) · [repair_prompt.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/agents/repair_prompt.py) |
| **F3 (Verification)**| `verify_healed` | Safe verification logic preventing false-positive successes. | [verify.py](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/harness/verify.py) |
| **G1-G3 (UI)** | Streamlit App | Interactive dashboard displaying pipeline states, before/after script diffs, screenshots, and logs. | [ui/](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/ui/) |

---

## 3. Architecture & Data Flow

When integrated, the pipeline follows the graph sequence defined in `graph/build.py`:

```
Discovery → ScriptGen → Execution ──► pass ──► END (Pass)
                              │
                           fail ▼
                     Error Diagnosis → Adaptive Repair ──► Execution (Re-run)
                                           │
                                     (Attempt count >= Max)
                                           ▼
                                       END (Give Up)
```

### State Integration
Every agent node expects and updates the shared `AgentState` object:
- `discovery` and `script_gen` yield the target `Flow` and initial Playwright `Script`.
- `execution` produces a `RunResult` (containing logs, screenshots, and status).
- If status is `"fail"`, `diagnosis` populates the `Diagnosis` field (kind, root_cause, suggested_fix).
- `repair` appends a `RepairAttempt` to history and replaces `state.script` with the updated code.

---

## 4. Technical Specifications

### 4.1. LLM Mock Config (`USE_MOCK=1`)
To run offline without hitting OpenRouter or depleting credits, set the environment variable:
```bash
$env:USE_MOCK="1"  # PowerShell
```
This forces [`model_for()`](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/config/__init__.py) to load `FakeModel` and fetch pre-canned role-specific JSONs or code blocks.

### 4.2. Error Classification (E1)
The system classifies errors into exactly four kinds:
1. `selector` — Target element tag or attribute changed/missing.
2. `timeout` — The page or loader delay exceeded bounds.
3. `missing_element` — Conditionally missing page section.
4. `flow_change` — Steps were reordered or split.

### 4.3. Script Verification (F3)
The verification hook confirms a heal ONLY if:
- `result.status == "pass"`
- `result.error` is `None`
- (Optional) Verification diffs match the target page state.

---

## 5. UI Layout

The Streamlit dashboard located at [`ui/app.py`](file:///d:/My-AI-Journey/Outskill-Engineering-Accelerator-14Days-Course/TeamHackathonProject/Team5_Hackathon/ui/app.py) contains two modes:
1. **Mock State Player (Demo Mode)**: A playback controller allowing manual visual stepping through:
   - Initial Discovery
   - First Run Failed
   - Error Diagnosed
   - Script Healed
2. **Live Graph Execution**: A trigger button running the compiled LangGraph pipeline dynamically.

---

## 6. Integration Steps for `develop`

When merging this branch into the `develop` branch, the integration points are:

1. **Graph Wiring**: In `graph/build.py`, ensure the conditional edges correctly transition to `diagnosis_node` and `repair_node` on failure:
   ```python
   g.add_node("diagnosis", diagnosis_node)
   g.add_node("repair", repair_node)
   ```
2. **Human-in-the-Loop Interrupt**: In `graph/build.py`, add a LangGraph `interrupt()` on the transition from `repair` back to `execution` if `state.hitl` is enabled.
3. **Harness Hook**: The Scoreboard pair's test runner can import `verify_healed` from `harness.verify` to grade healing success rates.
