# Scoreboard — auto-repair metrics (F2)

**Auto-repair rate: 25%** (1/4 initially-failed cases healed, 3 more flagged suspect by F3) — target >= 50% NOT MET

## By failure class

| Failure class | Attempted | Healed (verified) | Rate |
|---|---|---|---|
| missing_element | 2 | 0 | 0% |
| selector | 2 | 1 | 50% |

## Per-case detail

| Case | User | Expected class | Initial | Final | Repair attempts | Healed | Verified |
|---|---|---|---|---|---|---|---|
| smoke_login__baseline | standard_user | pass | pass | pass | 0 | no | None |
| smoke_add_to_cart__baseline | standard_user | pass | pass | pass | 0 | no | None |
| e2e_checkout__baseline | standard_user | pass | pass | pass | 0 | no | None |
| e2e_multi_item_checkout__baseline | standard_user | pass | pass | pass | 0 | no | None |
| e2e_sort_inventory__baseline | standard_user | pass | pass | pass | 0 | no | None |
| e2e_remove_from_cart__baseline | standard_user | pass | pass | pass | 0 | no | None |
| e2e_logout__baseline | standard_user | pass | pass | pass | 0 | no | None |
| checkout_problem_user | problem_user | missing_element | fail | pass | 1 | yes | False |
| checkout_performance_glitch_user | performance_glitch_user | timeout | pass | pass | 0 | no | None |
| checkout_error_user | error_user | selector | fail | pass | 1 | yes | False |
| checkout_locked_out_user | locked_out_user | missing_element | fail | pass | 1 | yes | False |
| checkout_broken_selector | standard_user | selector | fail | pass | 1 | yes | True |
