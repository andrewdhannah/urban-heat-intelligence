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
        assert "Source: FortyGuard" in await page.locator(".map-panel").inner_text()
        await page.locator(".source-control[data-source='fortyguard']").focus()
        assert await page.locator("[data-popover='fortyguard']").is_visible()
        assert "USED TO RANK" in await page.locator("[data-popover='fortyguard']").inner_text()
        await page.locator(".source-control[data-source='fortyguard']").hover()
        assert await page.locator("[data-popover='fortyguard']").is_visible()
        # Pointer can move into the disclosure without collapsing it.
        await page.locator("[data-popover='fortyguard']").hover()
        assert await page.locator("[data-popover='fortyguard']").is_visible()
        await page.locator(".source-control[data-source='fortyguard']").press("Escape")
        assert not await page.locator("[data-popover='fortyguard']").is_visible()
        assert await page.locator(".leaflet-interactive").count() > 0
        assert await page.evaluate("window.__lunaHeatmapFeatureCount") == 367
        assert await page.locator("#legend-min").inner_text() != "—"
        assert await page.locator("#legend-max").inner_text() != "—"
        styles = await page.locator(".leaflet-interactive").evaluate_all("els => [...new Set(els.map(e => getComputedStyle(e).fill))]")
        assert len(styles) > 1
        assert await page.evaluate("document.querySelectorAll('.leaflet-interactive').length > 0")
        assert "top thermal cluster" in (await page.locator("#answer-hero").inner_text()).lower()
        assert "Start with candidate 1" not in await page.locator("#answer-hero").inner_text()
        assert await page.locator(".brief-section").count() > 0
        await page.locator(".candidate-card").first.click()
        assert await page.locator(".candidate-card.focused").count() == 1
        await page.locator(".evidence-toggle").click()
        assert await page.locator(".chain-node").count() > 0
        assert "not included in historical Replay" in await page.locator("#brief-content").inner_text()
        assert "used_in_decision = false" in await page.locator("#context-content").inner_text()
        assert "Source: City of Phoenix GIS" in await page.locator(".context-panel").inner_text()
        assert "Source: Derived interpretation" in await page.locator(".brief-panel").inner_text()
        context = await page.locator("#context-content").inner_text()
        assert "Roosevelt Park" in context
        assert "No mapped park at candidate" in context
        assert "Portland Parkway" in context
        assert "Parks context unavailable" not in context
        assert await page.locator("#candidate-list").inner_text()
        assert "Humidity" not in str(await page.locator(".candidate-card").all_inner_texts())
        assert await page.locator("#replay-env-context").count() == 1
        assert await page.locator(".leaflet-interactive").count() > 0
        # Leaflet's SVG path event is covered by the runtime implementation;
        # verify the accessible measured-cell detail surface exists without
        # relying on synthetic DOM events.
        assert await page.locator("#cell-detail").count() == 1
        await page.locator("#map-focus-button").click()
        assert await page.locator("body.map-focus").count() == 1
        exit_button = page.locator("#focus-exit-button")
        assert await exit_button.is_visible()
        assert await exit_button.is_enabled()
        assert await exit_button.bounding_box()
        assert await page.locator(".candidate-marker").count() == 3
        await exit_button.click()
        assert await page.locator("body.map-focus").count() == 0
        assert await page.locator(".candidates-section").is_visible()
        assert await page.locator(".brief-panel").is_visible()
        await page.locator("#map-focus-button").click()
        await page.locator(".source-control[data-source='fortyguard']").focus()
        assert await page.locator("[data-popover='fortyguard']").is_visible()
        await page.keyboard.press("Escape")
        assert not await page.locator("[data-popover='fortyguard']").is_visible()
        assert await page.locator("body.map-focus").count() == 1
        await page.keyboard.press("Escape")
        assert await page.locator("body.map-focus").count() == 0
        await page.locator("#question-input").fill("Which trees would cool this area most?")
        await page.locator("#question-form button").click()
        assert "does not estimate the cooling effect" in await page.locator("#analyst-result").inner_text()
        assert "Why it matters:" in await page.locator("#analyst-result").inner_text()
        assert "does not estimate intervention effectiveness" in await page.locator("#analyst-result").inner_text()
        await page.locator("#question-input").fill("show live data")
        await page.locator("#question-form button").click()
        assert "Switching to Live mode." in await page.locator("#analyst-result").inner_text()
        await page.wait_for_timeout(300)
        assert await page.locator("#btn-live").get_attribute("aria-pressed") == "true"
        assert await page.locator("#replay-env-context").count() == 0
        # Environmental provenance: candidate cards must not imply per-candidate env_params
        all_card_text = str(await page.locator(".candidate-card").all_inner_texts())
        assert "Environmental parameters retrieved for this candidate" not in all_card_text
        assert "Humidity" not in all_card_text
        assert "Heat index" not in all_card_text
        assert "Apparent temp" not in all_card_text
        await page.keyboard.press("Tab")
        await page.keyboard.press("Enter")
        assert await page.locator(".candidate-card.focused").count() >= 1
        await page.locator("#btn-replay").click()
        await page.wait_for_timeout(700)
        assert await page.locator(".candidate-card").count() == 3
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert "FORTYGUARD_API_KEY" not in await page.content()
        assert not errors, errors
        await page.set_viewport_size({"width": 390, "height": 844})
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        print("LUNA_BROWSER: PASS")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
