# Scoreboard — auto-repair metrics (F2)

**Auto-repair rate: 0%** (0/3 initially-failed cases healed) — target >= 50% NOT MET

## By failure class

| Failure class | Attempted | Healed (verified) | Rate |
|---|---|---|---|
| missing_element | 2 | 0 | 0% |
| selector | 1 | 0 | 0% |

## Per-case detail

| Case | User | Expected class | Initial | Final | Repair attempts | Healed | Verified |
|---|---|---|---|---|---|---|---|
| checkout_standard_user | standard_user | pass | pass | pass | 0 | no | None |
| checkout_problem_user | problem_user | missing_element | fail | fail | 3 | no | None |
| checkout_performance_glitch_user | performance_glitch_user | timeout | pass | pass | 0 | no | None |
| checkout_error_user | error_user | selector | fail | fail | 3 | no | None |
| checkout_locked_out_user | locked_out_user | missing_element | fail | fail | 3 | no | None |
