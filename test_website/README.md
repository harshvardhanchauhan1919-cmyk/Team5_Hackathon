<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# Test Website

This contains the local Vite/React test website used by the self-healing browser automation demo.

View your app in AI Studio: https://ai.studio/apps/06d1fc94-e8a0-4af6-9eeb-bcab2f6a5f82

## Run Locally

**Prerequisites:**

- WSL with Linux Node.js 20+ and npm. This test website is a Vite/React app, so its dependencies are managed by `package.json` and npm, not by Python `uv`.
- A Gemini API key if you use the AI features.

1. Open a WSL shell and enter this folder:
   `cd /home/e2n055/Team5_Hackathon/test_website`
2. If you use `nvm`, load Node 20:
   `source ~/.nvm/nvm.sh && nvm use 20`
3. Install dependencies:
   `npm install`
4. Copy the environment template and set your key:
   `cp .env.example .env.local`
5. Set `GEMINI_API_KEY` in `.env.local` to your Gemini API key.
6. Run the app:
   `npm run dev`
7. Open:
   `http://localhost:3000`

## Break Modes

Break modes intentionally change the website at runtime so generated Playwright scripts can fail and trigger the healing loop. Add the `break` query parameter to the local URL.

Available modes:

- `cart_selector`: changes the cart button from `data-test="shopping-cart-link"` to `data-test="cart-link-v2"`.
- `continue_selector`: changes the checkout continue button from `data-test="continue"` to `data-test="continue-checkout"`.
- `complete_selector`: changes the order completion header from `data-test="complete-header"` to `data-test="order-complete-title"`.
- `checkout_delay`: delays navigation from checkout information to checkout overview by 3000 ms.

Examples:

```text
http://localhost:3000?break=cart_selector
http://localhost:3000?break=continue_selector
http://localhost:3000?break=complete_selector
http://localhost:3000?break=checkout_delay
```

No break mode is active when the `break` query parameter is missing or not one of the supported values.

## Windows Users

Run the test website through WSL, not Windows PowerShell or Windows cmd. Windows `npm` can create incompatible `node_modules` inside this WSL project.

From Windows PowerShell, start the dev server through WSL:

```powershell
wsl.exe --cd /home/e2n055/Team5_Hackathon/test_website bash -lc 'source ~/.nvm/nvm.sh && nvm use 20 && npm install && npm run dev'
```

Then open:

```text
http://localhost:3000
```

To run with a break mode, open one of the break-mode URLs, for example:

```text
http://localhost:3000?break=cart_selector
```

### WSL Only

Run these commands from WSL, not Windows PowerShell or Windows cmd. Windows npm can create incompatible `node_modules` inside a WSL project.

Check that Linux binaries are being used:

`which node && which npm`

They should resolve under `/home/...`, such as `~/.nvm/versions/node/...`, not `/mnt/c/...`.
