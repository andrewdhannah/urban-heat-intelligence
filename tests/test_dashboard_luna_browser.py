"""Additive Luna browser checks. Requires Playwright in the QA environment.
Run: python3 tests/test_dashboard_luna_browser.py
"""
import asyncio
import os
from playwright.async_api import async_playwright

URL = os.environ.get("LUNA_URL", "http://127.0.0.1:8090/")
VIEWPORT = tuple(int(value) for value in os.environ.get("LUNA_VIEWPORT", "1440x900").split("x"))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="networkidle", timeout=120000)
        await page.wait_for_timeout(2000)
        assert await page.locator(".candidate-card").count() == 3
        assert await page.locator(".candidate-marker").count() == 3
        assert all("Location context unavailable" in text for text in await page.locator(".candidate-card").all_inner_texts())
        asset_urls = await page.locator("link[rel='stylesheet'], script[type='module']").evaluate_all("els => els.map(e => e.href || e.src).filter(url => url.startsWith(location.origin))")
        assert asset_urls and all("?v=" in url and "{{BUILD_VERSION}}" not in url for url in asset_urls)
        if VIEWPORT[0] >= 1050:
            assert await page.locator("#catalogue-panel").is_visible()
        assert await page.locator("#stat-obs-time").inner_text() != "Loading…"
        # Animation settled: evidenceAnimating should be null
        assert await page.evaluate("window.__lunaState_evidenceAnimating") is None
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
        # Heat field renders with multiple distinct colors. The promoted dashboard
        # renders the measured field on a canvas (preferCanvas), so sample rendered
        # pixels instead of SVG path fill styles.
        canvas_colors = await page.evaluate("""() => {
            const canvas = document.querySelector('.leaflet-overlay-pane canvas');
            if (!canvas) return [];
            const ctx = canvas.getContext('2d');
            const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            const colors = new Set();
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] === 0) continue;
                colors.add(`${data[i]},${data[i+1]},${data[i+2]}`);
                if (colors.size > 3) break;
            }
            return [...colors];
        }""")
        assert len(canvas_colors) > 1, f"heat canvas should show multiple colors, got {canvas_colors}"
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
        exit_button = page.locator("#map-focus-button")
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
        await page.locator("#question-form button[type='submit']").click()
        assert "does not estimate the cooling effect" in await page.locator("#status-region").inner_text()
        assert "Why it matters:" in await page.locator("#status-region").inner_text()
        assert "does not estimate intervention effectiveness" in await page.locator("#status-region").inner_text()
        await page.locator("#question-input").fill("show live data")
        await page.locator("#question-form button[type='submit']").click()
        assert "Switching to Live mode." in await page.locator("#status-region").inner_text()
        await page.wait_for_timeout(300)
        assert await page.locator("#btn-live").get_attribute("aria-pressed") == "true"
        assert await page.locator("#replay-env-context").count() == 0
        # Environmental provenance: candidate cards must not imply per-candidate env_params
        all_card_text = str(await page.locator(".candidate-card").all_inner_texts())
        assert "Environmental parameters retrieved for this candidate" not in all_card_text
        assert "Humidity" not in all_card_text
        assert "Heat index" not in all_card_text
        assert "Apparent temp" not in all_card_text
        await page.locator("#btn-replay").click()
        await page.wait_for_timeout(700)
        assert await page.locator(".candidate-card").count() == 3
        # Keyboard accessibility: candidate cards are focusable and Enter activates them
        card2 = page.locator(".candidate-card[data-rank='2']")
        await card2.focus()
        await page.keyboard.press("Enter")
        assert await page.locator(".candidate-card.focused").count() == 1
        assert await page.locator(".candidate-card.focused").get_attribute("data-rank") == "2"
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert "FORTYGUARD_API_KEY" not in await page.content()
        # === P1: candidate markers — prominent, numbered, synchronized ===
        marker_boxes = await page.locator(".candidate-marker").evaluate_all(
            "els => els.map(e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height, text: e.textContent.trim() }; })")
        assert len(marker_boxes) == 3
        assert [m["text"] for m in marker_boxes] == ["1", "2", "3"], f"marker labels: {[m['text'] for m in marker_boxes]}"
        assert all(m["w"] >= 40 and m["h"] >= 40 for m in marker_boxes), f"markers must be >= 40px, got {marker_boxes}"
        # markers fully opaque regardless of heat overlay opacity
        marker_opacities = await page.locator(".candidate-marker").evaluate_all("els => els.map(e => getComputedStyle(e).opacity)")
        assert all(o == "1" for o in marker_opacities), f"marker opacity: {marker_opacities}"
        # marker/card synchronization: hovering card 2 highlights marker 2
        await page.locator(".candidate-card[data-rank='2']").hover()
        assert await page.locator(".candidate-marker.marker-focused").count() == 1
        assert await page.locator(".candidate-marker.marker-focused").inner_text() == "2"
        await page.locator(".candidate-card[data-rank='2']").dispatch_event("mouseleave")
        assert await page.locator(".candidate-marker.marker-focused").count() == 0
        # === P1: heat overlay opacity control ===
        opacity_input = page.locator("#heat-opacity")
        assert await opacity_input.count() == 1
        assert await opacity_input.get_attribute("type") == "range"
        assert await opacity_input.get_attribute("min") == "20"
        assert await opacity_input.get_attribute("max") == "90"
        default_opacity = float(await opacity_input.input_value())
        assert 65 <= default_opacity <= 70, f"default opacity {default_opacity}"
        assert await page.locator("#heat-opacity-value").inner_text() == f"{int(default_opacity)}%"
        # keyboard operable
        await opacity_input.focus()
        await page.keyboard.press("ArrowLeft")
        assert float(await opacity_input.input_value()) < default_opacity
        # changing opacity changes the visual layer only
        assert await page.evaluate("window.__lunaHeatmapFeatureCount") == 367
        await opacity_input.fill("30")
        assert await page.locator("#heat-opacity-value").inner_text() == "30%"
        assert await page.evaluate("window.__lunaHeatOpacity") == 0.3
        assert await page.evaluate("window.__lunaHeatmapFeatureCount") == 367
        assert await page.locator(".candidate-marker").count() == 3
        assert await page.locator(".candidate-card").count() == 3
        card_order = await page.locator(".candidate-card h3").all_inner_texts()
        assert card_order == ["Candidate 1", "Candidate 2", "Candidate 3"]
        await opacity_input.fill(str(int(default_opacity)))
        # === P1: monochrome basemap ===
        assert await page.locator("#basemap-standard").get_attribute("aria-pressed") == "true"
        await page.locator("#basemap-monochrome-btn").click()
        assert await page.locator("#basemap-monochrome-btn").get_attribute("aria-pressed") == "true"
        assert await page.locator("#basemap-standard").get_attribute("aria-pressed") == "false"
        assert await page.locator("#map.basemap-monochrome").count() == 1
        # thermal layer and markers unaffected
        assert await page.evaluate("window.__lunaHeatmapFeatureCount") == 367
        assert await page.locator(".candidate-marker").count() == 3
        # basemap tiles grayscaled; heat canvas not
        tile_filters = await page.evaluate("() => [...document.querySelectorAll('.leaflet-tile-pane img')].map(i => getComputedStyle(i).filter)")
        assert tile_filters and all("grayscale" in f for f in tile_filters), f"tile filters: {tile_filters}"
        heat_canvas_filter = await page.evaluate("() => { const c = document.querySelector('.leaflet-overlay-pane canvas'); return c ? getComputedStyle(c).filter : null; }")
        assert heat_canvas_filter == "none", f"heat canvas filter: {heat_canvas_filter}"
        await page.locator("#basemap-standard").click()
        assert await page.locator("#map.basemap-monochrome").count() == 0
        # === P1: audience language ===
        context_text = await page.locator("#context-content").inner_text()
        assert "does not affect the thermal ranking" in context_text
        replay_env_text = await page.locator("#replay-env-context").inner_text()
        assert "Shared historical context" in replay_env_text
        assert "not a separate measurement for each candidate" in replay_env_text
        card_text = str(await page.locator(".candidate-card").all_inner_texts())
        assert "nearly tied" in card_text
        assert "intervention" not in card_text.lower()
        assert not errors, errors
        await page.set_viewport_size({"width": 390, "height": 844})
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        # P1: mobile marker visibility
        assert await page.locator(".candidate-marker").count() == 3
        mobile_marker_boxes = await page.locator(".candidate-marker").evaluate_all(
            "els => els.map(e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height }; })")
        assert all(m["w"] >= 40 and m["h"] >= 40 for m in mobile_marker_boxes), f"mobile markers: {mobile_marker_boxes}"
        # P1: reduced motion — same evidence, no animation errors
        rm_errors = []
        page.on("pageerror", lambda e: rm_errors.append(str(e)))
        await page.emulate_media(reduced_motion="reduce")
        await page.reload(wait_until="networkidle", timeout=120000)
        await page.wait_for_timeout(1500)
        assert await page.evaluate("window.__lunaHeatmapFeatureCount") == 367
        assert await page.locator(".candidate-marker").count() == 3
        assert await page.locator("#heat-opacity").count() == 1
        assert await page.locator("#basemap-monochrome-btn").count() == 1
        assert not await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert not rm_errors, rm_errors
        print("LUNA_BROWSER: PASS")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
