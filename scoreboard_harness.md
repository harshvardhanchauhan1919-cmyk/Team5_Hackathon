**Context**
- this is part of the total project (see full github)
- consider readme.md

**Coding constraints**
- all code to be placed in the /harness directory
- all code is in python

**EPIC C**
- GOAL: Swag Labs target & break harness *(starts at minute zero)* QA's lane; needs only "hello browser," not the schema.
- USER STORIES:
-- C1: map the checkout flow and capture the full `data-test` selector set (that's the baseline scripts are generated against)
-- C2: the **break-user matrix** — empirically verify which buggy user (`problem_user`, `performance_glitch_user`, `error_user`, `locked_out_user`) triggers which failure class; run it, don't trust the docs. 
-- C3: HAR/trace recording + deterministic replay so CI and the recorded demo never depend on the live site.


# Epic E — Hero loop *(the whole judged story)*
- E4: the **flow-change beat** — Swag Labs' buggy users don't reorder steps, so one tiny local fixture or Playwright route-intercept covers that one failure class.

# Epic F — Harness, scoreboard & metrics *(the proof)*
F1: harness runner over `{flow × break}` cases. 
F2: the metrics table showing ≥50% auto-repair and which classes healed — this is the scoreboard that goes in the video and README.
F3: "healed is truly healed" verification (a repair that passes for the wrong reason is a demo-killer) + Regression Monitor **only if ahead**.
