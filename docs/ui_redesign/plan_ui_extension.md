**Goal**
- extend the streamlit webpage expose furhter informantion

**Coding constraints**
- all code to be placed in the /ui directory
- all code is in python
- work with the current streamlit webpage

**Todo**
[x] At the end of the webpage, when selector.py has finished, show the output also on the webpage
-- Add a section with title-name ‘Selector baseline – {name}’ where name is the flow that was just tested
--- In this section
---- Add a comment line below the title-name, equal to the comment line in the selector.md file that is created in selector.py
---- Add a table to show [#, Action, Selector, Description, Verified, Duration (s)] equal to the selector.md file that is created in selector.py

Implemented in `ui/components/selector_baseline.py` (`render_selector_baseline()`), wired
into `ui/app.py` after the gallery section. A "Run Selector Baseline (C1)" button triggers
`harness.selectors.capture_and_verify()` (a real Playwright run against Swag Labs) and
caches the result in `st.session_state` so it persists across reruns. Verified live in a
running Streamlit session: title renders as "Selector baseline – Login -> add backpack ->
checkout -> finish" (from `CHECKOUT_FLOW.name`), the caption line matches `selectors.md`'s
comment text exactly, and the table matches all 17 rows of the generated baseline.

[x] At the end of the webpage, when metrics.py has finished, show the output also on the webpage:
-- Add a section with title-name ‘Scoreboard — auto-repair metrics’ 
--- In this section
---- Add a conclusion line below the title-name, equal to the conclusion line in the report.md file that is created in metric.py
---- Add a sub-section with title “By failure class” with a  table showing [Failure class, Attempted, Healed (verified), Rate] equal to the ‘By failure class’ table in report.md file that is created in metric.py
---- Add a sub-section with title “Per-case detail” with a table showing [Case, User, Expected class, Initial, Final, Repair attempts Healed, Verified] equal to the ‘Per-case detail’ table in report.md file that is created in metric.py

Implemented in `ui/components/scoreboard.py` (`render_scoreboard()`), wired into
`ui/app.py` right after the selector baseline section. Reads `harness/report.json` via
`harness.metrics.load_results()` + `summarize()` (no live browser run needed — it's the
same data `harness/report.md` is generated from) with a "Refresh Scoreboard (F2)" button
to reload after a new harness run. Verified live: conclusion line, "By failure class"
table, and "Per-case detail" table all match `harness/report.md` exactly.
