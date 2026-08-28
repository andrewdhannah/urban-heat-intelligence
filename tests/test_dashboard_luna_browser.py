"""Additive Luna browser checks. Requires Playwright in the QA environment.
Run: python3 tests/test_dashboard_luna_browser.py
"""
import asyncio
import os
from playwright.async_api import async_playwright

URL = os.environ.get("LUNA_URL", "http://127.0.0.1:8090/")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="networkidle", timeout=120000)
        await page.wait_for_timeout(1000)
        assert await page.locator(".candidate-card").count() == 3
        assert await page.locator(".candidate-marker").count() == 3
        assert await page.locator("#stat-obs-time").inner_text() != "Loading…"
        assert await page.locator(".leaflet-interactive").count() > 0
        assert await page.locator("#legend-min").inner_text() != "—"
        assert await page.locator("#legend-max").inner_text() != "—"
        assert "top thermal cluster" in (await page.locator("#answer-hero").inner_text()).lower()
        assert "Start with candidate 1" not in await page.locator("#answer-hero").inner_text()
        assert await page.locator(".brief-section").count() > 0
        await page.locator(".candidate-card").first.click()
        assert await page.locator(".candidate-card.focused").count() == 1
        await page.locator(".evidence-toggle").click()
        assert await page.locator(".chain-node").count() > 0
        assert "not included in historical Replay" in await page.locator("#brief-content").inner_text()
        assert "used_in_decision = false" in await page.locator("#context-content").inner_text()
        assert await page.locator("#candidate-list").inner_text()
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert "FORTYGUARD_API_KEY" not in await page.content()
        assert not errors, errors
        await page.set_viewport_size({"width": 390, "height": 844})
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        print("LUNA_BROWSER: PASS")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
