<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

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

### WSL Only

Run these commands from WSL, not Windows PowerShell or Windows cmd. Windows npm can create incompatible `node_modules` inside a WSL project.

Check that Linux binaries are being used:

`which node && which npm`

They should resolve under `/home/...`, such as `~/.nvm/versions/node/...`, not `/mnt/c/...`.
