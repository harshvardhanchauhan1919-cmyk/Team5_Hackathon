## Update Todos
- [x] Write harness/step_executor.py (shared step runner + failure classifier)
- [x] Write harness/selectors.py (C1 baseline flow + live capture/verify)
- [x] Write harness/break_matrix.py (C2 buggy-user probe)
- [x] Write harness/replay.py (C3 HAR record/replay)
- [x] Run C1 live against saucedemo.com to generate selectors.md
- [x] Run C2 live to generate break_matrix.yaml + evidence screenshots
- [x] Run C3 to record HARs and verify replay matches live classification

Epic C is built, all under /harness, and verified live against saucedemo.com (not from docs) — ruff clean, existing test suite still green.

## What's there:
- harness/step_executor.py — shared step runner + root-cause classifier used by all three tickets. Classifies failures by checking (in order): visible [data-test="error"] banner → missing_element; forward progress after a grace window → timeout; neither → selector.
- harness/selectors.py (C1) — the 17-step checkout flow baseline (CHECKOUT_FLOW, typed as Flow/Step from the frozen schema), live-verified against standard_user. Generates harness/selectors.md.
- harness/break_matrix.py (C2) — probes all 4 buggy users + control live, writes harness/break_matrix.yaml with evidence screenshots under harness/fixtures/break_matrix/.
- harness/replay.py (C3) — records HAR fixtures (harness/fixtures/har/) and replays them fully offline; verify diffs replay classification against the live break-matrix result.

## Real, empirically-observed results (not assumed from docs):
| User | Observed class | Root cause |
|---|---|---|
| standard_user | pass | control |
| problem_user | missing_element | checkout form rejects "Last Name" — banner: "Error: Last Name is required" |
| performance_glitch_user | timeout | login click times out, but the page had already navigated — just slow |
| error_user | selector order-complete | confirmation never renders, no banner, no forward progress |
| locked_out_user | missing_element | banner: "Epic sadface: Sorry, this user has been locked out." |

All 5 HAR replays reproduced the exact same classification as the live run (python -m harness.replay verify → all OK).

One thing worth flagging to the team: this build put fixtures/ under harness/fixtures/ per this ticket's stated constraint, which conflicts with BRANCH_OWNERSHIP.md's top-level fixtures/. I noted this in the earlier PRD as an open question — worth a quick team call before other lanes (Diagnosis, CI) start depending on a path.
