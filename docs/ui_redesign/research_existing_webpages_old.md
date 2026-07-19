# Research — existing webpages used by this application

This application is a self-healing Playwright automation agent (see [README.md](README.md)).
It targets exactly one external site — **Swag Labs** (`https://www.saucedemo.com/`), a public
e-commerce demo built for QA practice — and drives it through a fixed set of pages while
logged in as different accounts (`standard_user` plus four intentionally-buggy accounts). No
other external site or URL is referenced anywhere in the codebase (verified by grepping the
whole repo for URLs/hostnames).

The pages below were confirmed live: each URL was walked with Playwright in this session
(`page.goto` + real clicks) and the exact resulting `page.url` was recorded, rather than assumed
from the code or docs.

---

## 1. Login page — `https://www.saucedemo.com/`

**Code locations:**
- [hello_world/hello_browser.py:20](hello_world/hello_browser.py#L20) — the "hello browser" smoke test logs in as `standard_user`.
- [agents/discovery.py:28](agents/discovery.py#L28), [agents/discovery.py:47](agents/discovery.py#L47), [agents/discovery.py:63-69](agents/discovery.py#L63-L69) — `DEFAULT_URL`, the `crawl()` function's first `page.goto`, and the `_login()` step-builder shared by every catalog flow.
- [harness/selectors.py:18](harness/selectors.py#L18), [harness/selectors.py:22-27](harness/selectors.py#L22-L27) — `TARGET_URL` and the first two steps of the C1 baseline flow (`CHECKOUT_FLOW`).
- [harness/cases.py:25](harness/cases.py#L25) — `DEFAULT_TARGET_URL` used to configure each harness break-user case.
- [fixtures/flow_catalog.json](fixtures/flow_catalog.json) — every frozen catalog flow's `target_url` and first `goto` step.
- [ui/mock_state.py:20-25](ui/mock_state.py#L20-L25) — mock UI fixture step used to render the pipeline view without a live run.
- [tools/mock_llm.py:78](tools/mock_llm.py#L78) — the LLM mock's canned "repaired" script also opens this page.

**What it does:** This is the entry point for every single flow in the system — nothing else can be tested until the pipeline logs in here. The page exposes a username field (`[data-test="username"]`), a password field (`[data-test="password"]`), and a login button (`[data-test="login-button"]`); the app fills the first two with whichever account the current case targets (`standard_user` for the happy path, or one of `problem_user` / `performance_glitch_user` / `error_user` / `locked_out_user` when deliberately probing a failure class) and clicks the button. This is also the page the "break-user matrix" (Epic C2, [harness/break_matrix.py](harness/break_matrix.py)) uses to empirically observe how each buggy account actually fails, and the page Discovery's `crawl()` function reads first to inventory which `data-test` elements genuinely exist before assembling the flow catalog.

---

## 2. Inventory / Products page — `https://www.saucedemo.com/inventory.html`

**Code locations:**
- [agents/discovery.py:52](agents/discovery.py#L52), [agents/discovery.py:84-86](agents/discovery.py#L84-L86), [agents/discovery.py:110-118](agents/discovery.py#L110-L118), [agents/discovery.py:131-140](agents/discovery.py#L131-L140) — crawl step after login, the `_add()` step-builder for "add to cart", the `smoke_add_to_cart` catalog flow, and the `e2e_sort_inventory` catalog flow.
- [harness/selectors.py:31-36](harness/selectors.py#L31-L36) — the baseline's `inventory-container` visibility check, the "add Sauce Labs Backpack to cart" click, and the cart-badge-increments-to-1 assertion.
- [agents/diagnosis_prompt.py:53](agents/diagnosis_prompt.py#L53) — used as a worked example in the Diagnosis agent's system prompt (a canned log line showing a timeout on this page, teaching the LLM what a `timeout`-class failure looks like here).
- [fixtures/flow_catalog.json](fixtures/flow_catalog.json) — steps for `smoke_add_to_cart` and `e2e_sort_inventory`.

**What it does:** This is the product catalog shown immediately after a successful login. The app interacts with it in two ways depending on the flow: adding an item to the cart via a per-product `[data-test="add-to-cart-<item-slug>"]` button (verified afterwards by checking `[data-test="shopping-cart-badge"]` increments), and — for the `e2e_sort_inventory` regression flow — exercising the `[data-test="product-sort-container"]` dropdown to sort by price. It's also the first page Discovery's live crawler reads after login to discover which products/selectors actually exist, which is what lets the flow catalog be built from real DOM structure instead of a hand-typed guess.

---

## 3. Cart page — `https://www.saucedemo.com/cart.html`

**Code locations:**
- [agents/discovery.py:53](agents/discovery.py#L53), [agents/discovery.py:99](agents/discovery.py#L99), [agents/discovery.py:141-152](agents/discovery.py#L141-L152) — the crawl's cart-page visit, the shared `open_cart` step, and the `e2e_remove_from_cart` catalog flow.
- [harness/selectors.py:37-39](harness/selectors.py#L37-L39) — the baseline's "open cart" click and the assertion that the checkout button is visible.
- [fixtures/flow_catalog.json](fixtures/flow_catalog.json) — steps for `e2e_checkout`, `e2e_multi_item_checkout`, and `e2e_remove_from_cart`.

**What it does:** Reached via the `[data-test="shopping-cart-link"]` icon, this page lists whatever was just added to the cart and exposes the `[data-test="checkout"]` button that begins the purchase flow. For the `e2e_remove_from_cart` regression flow specifically, the app also clicks a per-item `[data-test="remove-<item-slug>"]` button here and checks that `[data-test="continue-shopping"]` is still present afterwards — proving cart mutations don't break the page. Every checkout-oriented flow in the catalog passes through this page on its way to the checkout steps below.

---

## 4. Checkout: Your Information (step one) — `https://www.saucedemo.com/checkout-step-one.html`

**Code locations:**
- [agents/discovery.py:72-78](agents/discovery.py#L72-L78) — the `_checkout_info()` step-builder shared by every checkout flow (start checkout, fill first/last name + zip, continue).
- [harness/selectors.py:40-47](harness/selectors.py#L40-L47) — the equivalent steps in the C1 baseline (`checkout` click, `firstName`/`lastName`/`postalCode` fills, `continue` click).
- [agents/diagnosis_prompt.py:77-89](agents/diagnosis_prompt.py#L77-L89) — used as the worked example for the Diagnosis agent's `flow_change` failure class (a canned log line referencing `/checkout-step-one.html` to teach the LLM what a reordered-flow failure looks like on this page).
- [fixtures/flow_catalog.json](fixtures/flow_catalog.json) — steps for `e2e_checkout` and `e2e_multi_item_checkout`.

**What it does:** This is the shipping-details form: three required fields (`firstName`, `lastName`, `postalCode`) and a `continue` button. Every generated script fills these with placeholder values (`"Jane"`/`"Doe"`/`"12345"` in Discovery's catalog builder, `"Test"`/`"User"`/`"12345"` in the harness baseline) before proceeding. This page is also where the empirically-observed `problem_user` bug actually surfaces (see [harness/break_matrix.yaml](harness/break_matrix.yaml)): the site rejects the form with an `"Error: Last Name is required"` banner even though the last-name field was filled, which C2's break-user matrix classified as a `missing_element` failure.

---

## 5. Checkout: Overview (step two) — `https://www.saucedemo.com/checkout-step-two.html`

**Code locations:**
- [agents/discovery.py:79](agents/discovery.py#L79) — the "finish order" click in `_checkout_info()`.
- [harness/selectors.py:48-50](harness/selectors.py#L48-L50) — the baseline's assertion that the `finish` button is visible, followed by the click.

**What it does:** This page shows an order summary (items, prices, tax, total) and a single `[data-test="finish"]` button that submits the order. The app doesn't read or verify any of the summary content — it treats this purely as a pass-through step, asserting only that the `finish` button renders before clicking it, then moving on to the completion page.

---

## 6. Checkout: Complete — `https://www.saucedemo.com/checkout-complete.html`

**Code locations:**
- [agents/discovery.py:80](agents/discovery.py#L80) — the `expect_visible` check on `[data-test="complete-header"]` that closes every checkout catalog flow.
- [harness/selectors.py:51-52](harness/selectors.py#L51-L52) — the equivalent final assertion in the C1 baseline.

**What it does:** This is the terminal success page ("Thank you for your order!"), and its sole role in the system is as the pass/fail oracle for every checkout-shaped flow: the app asserts `[data-test="complete-header"]` is visible here, and if that assertion fails (timeout, missing element, or the page never being reached at all), the run is classified as failed and — in the live pipeline — handed to the Diagnosis/Repair loop. Reaching this page is what "the flow passed" means everywhere in this codebase (the harness scoreboard, the Execution node's `RunResult.status`, and the UI's pass/fail indicator all bottom out at this one check).

---

## Not a separate page, but worth noting

**Logout** (`e2e_logout` in [agents/discovery.py:153-162](agents/discovery.py#L153-L162) and [fixtures/flow_catalog.json](fixtures/flow_catalog.json)) doesn't navigate to a new URL — it opens the in-page burger menu (`#react-burger-menu-btn`) and clicks `[data-test="logout-sidebar-link"]`, which routes the SPA back to the login page above (`https://www.saucedemo.com/`) rather than loading a distinct URL. Swag Labs is a single-page React application (confirmed via the HAR recordings in [harness/fixtures/har/](harness/fixtures/har/), which show only one HTML document fetched per session, with all six "pages" above being client-side view transitions rather than separate server requests) — so every "page" in this document is a logical/DOM view identified by its `data-test` attributes and resulting `page.url`, not a distinct HTTP request.
