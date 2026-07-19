# Swag Labs checkout flow — selector baseline (C1)

Verified live against https://www.saucedemo.com/ as `standard_user`.
This is the ground truth Script Generator generates against and Diagnosis diffs against.

| # | Action | Selector | Description | Verified | Duration (s) |
|---|---|---|---|---|---|
| 0 | goto | — | Open Swag Labs login page | OK | 0.486 |
| 1 | fill | `[data-test="username"]` | Enter username | OK | 0.04 |
| 2 | fill | `[data-test="password"]` | Enter password | OK | 0.006 |
| 3 | click | `[data-test="login-button"]` | Submit login | OK | 0.065 |
| 4 | assert_visible | `[data-test="inventory-container"]` | Land on inventory page | OK | 0.008 |
| 5 | click | `[data-test="add-to-cart-sauce-labs-backpack"]` | Add Sauce Labs Backpack to cart | OK | 0.023 |
| 6 | assert_text | `[data-test="shopping-cart-badge"]` | Cart badge increments to 1 | OK | 0.007 |
| 7 | click | `[data-test="shopping-cart-link"]` | Open cart | OK | 0.047 |
| 8 | assert_visible | `[data-test="checkout"]` | Cart page shows checkout button | OK | 0.005 |
| 9 | click | `[data-test="checkout"]` | Begin checkout | OK | 0.042 |
| 10 | fill | `[data-test="firstName"]` | Enter first name | OK | 0.007 |
| 11 | fill | `[data-test="lastName"]` | Enter last name | OK | 0.009 |
| 12 | fill | `[data-test="postalCode"]` | Enter postal code | OK | 0.006 |
| 13 | click | `[data-test="continue"]` | Continue to overview | OK | 0.048 |
| 14 | assert_visible | `[data-test="finish"]` | Overview page shows finish button | OK | 0.005 |
| 15 | click | `[data-test="finish"]` | Finish checkout | OK | 0.043 |
| 16 | assert_visible | `[data-test="complete-header"]` | Order complete confirmation shown | OK | 0.006 |
