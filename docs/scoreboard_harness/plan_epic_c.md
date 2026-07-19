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
