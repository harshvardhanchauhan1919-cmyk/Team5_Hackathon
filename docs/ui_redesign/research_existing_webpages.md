# Research — webpages this application renders

This is a different question from [research_existing_webpages_old.md](research_existing_webpages_old.md),
which documented the external site the agent *automates against* (Swag Labs). This document covers
the webpage(s) **this application itself renders** — its own operator-facing dashboard, live-verified
by actually launching it and screenshotting it in this session (`streamlit run ui/app.py`, then driven
with Playwright), not assumed from reading the code alone.

## Tech stack

The dashboard is a single **Streamlit** app (`streamlit>=1.37.0` per [requirements.txt](requirements.txt);
`1.59.2` is what's installed) — a Python framework that turns a plain Python script into a server-rendered,
reactive web page: Streamlit runs `ui/app.py` top-to-bottom on every user interaction (a click, a dropdown
change) and diffs the result into the DOM itself, so there is no client-side framework (no React/Vue),
no routing library, and no separate frontend build step. All markup is either produced by Streamlit's own
widget API (`st.sidebar`, `st.columns`, `st.tabs`, `st.code`, `st.image`, …) or hand-written HTML/CSS
injected directly via `st.html()`. Visual styling is a custom dark "glassmorphic" theme written in plain
CSS ([ui/components/theme.css](ui/components/theme.css)) and injected into the page's `<style>` tag at
load time. There is exactly one Streamlit entry-point script (`ui/app.py`) — Streamlit calls this a
single-page app; the multiple "pages" described below are sections/tabs within that one page, not
separate URLs or routes.

---

## 1. Main dashboard page — `ui/app.py`

**Code location:** [ui/app.py](ui/app.py) (`main()`, lines 35-149), styling loaded from
[ui/components/theme.css](ui/components/theme.css) via `load_css()` (lines 26-32).

**What it does:** This is the single page Streamlit serves (default `http://localhost:8501` once launched
per [TESTING_HEALING_LOOP.md:90](TESTING_HEALING_LOOP.md#L90)). It sets the browser tab's title/icon
(`st.set_page_config`, a 🧠 emoji, wide layout), injects the custom theme CSS, and renders a header
("Self-Healing Browser Automation"). The left sidebar is the control panel: an **Operation Mode** dropdown
switches between "Mock State Player (Demo)" — which lets you scrub through four canned pipeline states
(`state_pending` / `state_failed` / `state_diagnosed` / `state_healed` from
[ui/mock_state.py](ui/mock_state.py)) via a radio button, entirely offline — and "Live Graph Execution",
which on button click actually imports `graph.build.build_graph()` and invokes the real LangGraph pipeline
against `state_pending`'s seed `Flow`/`Script`, reporting success/failure inline in the sidebar. A checkbox
and number input in the sidebar also let the operator toggle the human-in-the-loop gate (`hitl`) and the
repair attempt cap (`max_attempts`) directly on the `AgentState` before either mode runs. Whichever state
results (mock or live), `main()` hands it to the two components below to render the actual dashboard body.

---

## 2. Pipeline View section — `ui/components/pipeline.py`

**Code location:** [ui/components/pipeline.py](ui/components/pipeline.py) (`render_pipeline()`, the whole
file), styled by the `.pipeline-container` / `.pipeline-node` / `.pipeline-connector` rules in
[ui/components/theme.css:22-82](ui/components/theme.css#L22-L82).

**What it does:** Renders the five-stage agent pipeline (Discovery → Script Gen → Execution → Diagnosis
→ Repair) as a horizontal row of glowing status cards connected by lines, built entirely from one
`st.html()` call containing an f-string of hand-written HTML. Each node's status (`pending` / `active` /
`pass` / `fail`) is derived purely from which `AgentState` fields are populated — e.g. Execution shows
`ACTIVE` (blue glow) once `state.script` exists but `state.result` doesn't yet, then flips to `PASS`
(green) or `FAIL` (red) once `state.result.status` is known — and the connector line between two nodes
lights up once the downstream node has started. The Repair node additionally shows an "ATTEMPT n" pill
once at least one `RepairAttempt` exists. This is the "at a glance, did it heal" visual — confirmed live in
this session: it correctly showed all five nodes green with an "ATTEMPT 1" badge when the mock state
player was set to "4. Script Healed".

---

## 3. Artifact Gallery section — `ui/components/gallery.py`

**Code location:** [ui/components/gallery.py](ui/components/gallery.py) (`render_gallery()`, the whole
file).

**What it does:** Renders the detail view beneath the pipeline strip, in three stacked bordered containers.
First, if the current run failed (`state.result.status == "fail"`), it shows a red "Execution Failure
Detected" panel with the raw `Error` (kind, message, step index) next to the `Diagnosis` report (root
cause, confidence percentage, suggested fix) once one exists. Second, a "Script Code View" panel with two
tabs: "Original / Current Script" (`state.script.code` as a syntax-highlighted Python block) and "Repaired
Script History" (every `RepairAttempt` in `state.repair_attempts`, each with its own code block and
pass/fail result). Third, a "Screenshots & Logs" panel with its own two tabs — a screenshot grid (three
columns) pooling every screenshot path from the original run and all repair attempts, and a logs tab
printing the raw `logs` string from the original run and each repair attempt in turn. Note confirmed live
in this session: the screenshot tab doesn't render the actual PNG files on disk — it renders a
`placehold.co` placeholder image with the file path overlaid as text (see
[ui/components/gallery.py:91-95](ui/components/gallery.py#L91-L95)), so real screenshots captured by
Execution/Repair aren't visually shown yet, only referenced by filename.

---

## Verification

Launched with `streamlit run ui/app.py`, confirmed serving `HTTP 200` on `localhost:8501`, then driven
headlessly with Playwright to screenshot both the default "1. Initial Discovery" state and the
"4. Script Healed" state — both rendered exactly as the component code above describes (pipeline nodes
lighting up correctly per state, tabs and code blocks populating from the selected mock `AgentState`).
The server was stopped after verification.
