"""HELLO WORLD 1 — 'hello browser' (A3).

Proves Playwright works on your machine against the real target site.
Run:  python hello_world/hello_browser.py
Every laptop must run this GREEN before we split into lanes.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "artifacts"
OUT.mkdir(exist_ok=True)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set headless=False to watch it
        page = browser.new_page()

        page.goto("https://www.saucedemo.com/", timeout=60000)
        page.fill('[data-test="username"]', "standard_user")
        page.fill('[data-test="password"]', "secret_sauce")
        page.click('[data-test="login-button"]')
        page.screenshot(path=str(OUT / "01_inventory.png"))

        page.click('[data-test="add-to-cart-sauce-labs-backpack"]')
        page.click('[data-test="shopping-cart-link"]')
        page.click('[data-test="checkout"]')
        page.screenshot(path=str(OUT / "02_checkout.png"))

        browser.close()
    print("hello browser OK -> screenshots in", OUT)


if __name__ == "__main__":
    main()
