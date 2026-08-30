"""Runtime consumer checks for the R6-R2-R1 browser-closure pass.

Run with a Luna preview server:
  LUNA_URL=http://127.0.0.1:8090/ python3 tests/test_dashboard_luna_integrity_browser.py

Covers (all executable against the real renderer/browser):
  * three-state intersection semantics (SUCCESS / NO_RESULT / PROVIDER_FAILURE)
  * all nine canonical Explore questions -> intended intent, by click and by
    manual submission, with source-role semantics preserved
  * source-cell highlight for candidates 1/2/3 under the Canvas renderer,
    clearing on focus change, tied to the true tile_id
  * mobile result stacking (map above Current Read), resize round-trips
  * [hidden] application contract (catalogue collapse, NWS source line,
    evidence drawer, focus-exit control) incl. keyboard activation
  * NWS mutual mode-specificity (Replay historical vs Live forecast, mode
    switch/loading clearing) + DESK READOUT semantics preserved
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = os.environ.get("LUNA_URL", "http://127.0.0.1:8090/")

CATALOGUE = [
    ("Where should Phoenix prioritize cooling?", "identifies 3 candidate locations", "FortyGuard · measured evidence", "priority"),
    ("Compare the three candidates.", "FortyGuard measured field comparison", "FortyGuard · measured evidence", "compare"),
    ("Why are these locations nearly tied?", "no meaningful thermal winner", "FortyGuard · measured evidence", "tie"),
    ("What was the weather that afternoon?", "NWS station KPHX observed", "NWS · supplemental context", "weather"),
    ("Compare tree canopy.", "Phoenix GIS canopy", "Phoenix GIS · context only · not used to rank", "canopy"),
    ("Which candidates are near parks?", "Phoenix GIS parks", "Phoenix GIS · context only · not used to rank", "parks"),
    ("Where did this evidence come from?", "grounded in the loaded evidence chain", "Evidence chain · source roles preserved", "evidence"),
    ("What can this analysis not tell me?", "does not estimate the cooling effect", "Governed analytical scope", "unsupported"),
    ("Focus Candidate N.", "primary surface", "FortyGuard · measured evidence", "map"),
]


def make_live(seed):
    lp = json.loads(json.dumps(seed))
    lp["mode"] = "live"
    lp["visualization_source"] = "live"
    lp["conditions"] = dict(seed.get("conditions") or {})
    lp["conditions"]["ranking_status"] = "clear"
    lp["conditions"]["tie_threshold_celsius"] = 0.0
    lp["nws_context"] = {
        "provider": "NWS", "mode": "live",
        "conditions": {"temperature_f": 104, "short_forecast": "Mostly sunny",
                       "wind_speed": "9 mph", "wind_direction": "SW", "period_name": "This Afternoon"},
        "alerts": [], "alert_count": 0, "used_in_decision": False,
        "evidence_status": "supplemental_context", "source_endpoints": [],
    }
    lp["historical_nws_obs"] = None
    lp["historical_alerts"] = None
    lp["error"] = False
    return lp


class Router:
    def __init__(self, replay, live, delay_mode=None, fail_live=False):
        self.replay = replay
        self.live = live
        self.delay_mode = delay_mode
        self.fail_live = fail_live

    async def __call__(self, route):
        mode = "live" if "mode=live" in route.request.url else "replay"
        if self.delay_mode == mode:
            await asyncio.sleep(1.4)
        if self.fail_live and mode == "live":
            await route.fulfill(status=500, content_type="application/json",
                                body=json.dumps({"error": True, "mode": "live", "message": "mock failure"}))
            return
        body = json.dumps(self.live if mode == "live" else self.replay)
        await route.fulfill(status=200, content_type="application/json", body=body)


async def open_ready(browser, viewport, router):
    page = await browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
    await page.route("**/api/answer*", router)
    await page.goto(URL, wait_until="networkidle", timeout=120000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=30000)
    await page.wait_for_timeout(400)
    return page


def focus_escape_needed(question):
    return question.startswith("Focus Candidate")


async def assert_answer(page, question, phrase, source_sub):
    await page.wait_for_function(
        "document.querySelector('#status-region p') && document.querySelector('#status-region p').textContent.trim().length > 10",
        timeout=15000)
    answer = await page.locator("#status-region p").inner_text()
    source = await page.locator("#status-region small").inner_text()
    assert phrase in answer, f"{question}: answer {answer!r}"
    assert source_sub in source, f"{question}: source {source!r}"
    assert "DECK STATUS" not in await page.locator("#status-region").inner_text()
    assert "DESK READOUT" not in await page.locator("#status-region").inner_text()
    if focus_escape_needed(question):
        assert await page.locator("body.map-focus").count() == 1, question
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(200)


async def verify_explore_click(page):
    for question, phrase, source_sub, intent in CATALOGUE:
        btn = page.locator("#catalogue-panel button", has_text=question)
        assert await btn.count() == 1, question
        await btn.click()
        await assert_answer(page, question, phrase, source_sub)


async def verify_explore_manual(page):
    for question, phrase, source_sub, intent in CATALOGUE:
        await page.locator("#question-input").fill(question)
        await page.locator("#question-form button[type='submit']").click()
        await assert_answer(page, question, phrase, source_sub)


async def verify_highlight(page, seed):
    feats_before = await page.evaluate("window.__lunaHeatmapFeatureCount")
    for rank in (1, 2, 3):
        tile = next((c["tile_id"] for c in seed["ranked_candidates"] if c["rank"] == rank), None)
        assert tile is not None, rank
        await page.locator(f".candidate-card[data-rank='{rank}']").click()
        await page.wait_for_timeout(700)
        info = await page.evaluate("""() => {
            const cs = document.querySelectorAll('.leaflet-overlay-pane canvas.source-cell-highlight');
            return { count: cs.length, tileId: cs[0] && cs[0].dataset && cs[0].dataset.tileId,
                     focusedMarkers: document.querySelectorAll('.candidate-marker.marker-focused').length,
                     focusedCards: document.querySelectorAll('.candidate-card.focused').length };
        }""")
        assert info["count"] == 1, (rank, info)
        assert info["tileId"] == str(tile), (rank, info)
        assert info["focusedMarkers"] == 1 and info["focusedCards"] == 1, (rank, info)
    await page.locator(".candidate-card[data-rank='3']").dispatch_event("mouseleave")
    await page.wait_for_timeout(300)
    assert await page.evaluate("document.querySelectorAll('.leaflet-overlay-pane canvas.source-cell-highlight').length") == 0
    assert await page.evaluate("window.__lunaHeatmapFeatureCount") == feats_before


async def stacking_boxes(page):
    return await page.evaluate("""() => {
        const m = document.getElementById('map').getBoundingClientRect();
        const a = document.querySelector('.answer-rail').getBoundingClientRect();
        const p = document.querySelector('.map-panel').getBoundingClientRect();
        return { mapTop: m.top, railTop: a.top, mapH: m.height, panelH: p.height,
                 panelTop: p.top, scrollW: document.documentElement.scrollWidth,
                 clientW: document.documentElement.clientWidth };
    }""")


async def verify_mobile_stacking(browser, seed, live):
    router = Router(seed, live)
    page = await open_ready(browser, (390, 844), router)
    boxes = await stacking_boxes(page)
    assert boxes["mapTop"] < boxes["railTop"], boxes
    assert 250 <= boxes["mapH"] <= 460, boxes
    assert boxes["panelTop"] < boxes["railTop"], boxes
    assert boxes["scrollW"] <= boxes["clientW"], boxes
    await page.locator("#btn-live").click()
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'LIVE'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    boxes = await stacking_boxes(page)
    assert boxes["mapTop"] < boxes["railTop"], boxes
    assert 250 <= boxes["mapH"] <= 460, boxes
    await page.locator("#btn-replay").click()
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'REPLAY'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    boxes = await stacking_boxes(page)
    assert boxes["mapTop"] < boxes["railTop"], boxes
    await page.set_viewport_size({"width": 1440, "height": 900})
    await page.wait_for_timeout(600)
    side = await page.evaluate("""() => {
        const m = document.getElementById('map').getBoundingClientRect();
        const a = document.querySelector('.answer-rail').getBoundingClientRect();
        return { mapLeft: m.left, railLeft: a.left, mapTop: m.top, railTop: a.top };
    }""")
    assert side["mapLeft"] < side["railLeft"] and side["mapLeft"] != side["railLeft"], side
    await page.set_viewport_size({"width": 390, "height": 844})
    await page.wait_for_timeout(600)
    boxes = await stacking_boxes(page)
    assert boxes["mapTop"] < boxes["railTop"], boxes
    await page.close()


async def verify_hidden_contract(browser, seed, live):
    router = Router(seed, live)
    page = await open_ready(browser, (390, 844), router)
    panel = page.locator("#catalogue-panel")
    toggle = page.locator(".catalogue-toggle")
    assert await page.evaluate("getComputedStyle(document.getElementById('catalogue-panel')).display") == "none"
    assert await toggle.get_attribute("aria-expanded") == "false"
    await toggle.click()
    assert await page.evaluate("getComputedStyle(document.getElementById('catalogue-panel')).display") == "grid"
    assert await toggle.get_attribute("aria-expanded") == "true"
    await toggle.focus()
    await page.keyboard.press("Enter")
    assert await page.evaluate("getComputedStyle(document.getElementById('catalogue-panel')).display") == "none"
    assert await toggle.get_attribute("aria-expanded") == "false"
    assert await page.evaluate("getComputedStyle(document.getElementById('nws-source-line')).display") == "none"
    drawer = page.locator("#evidence-drawer")
    assert await page.evaluate("getComputedStyle(document.getElementById('evidence-drawer')).display") == "none"
    await page.locator("#evidence-toggle").click()
    assert await drawer.is_visible()
    await page.locator("#evidence-close").click()
    assert await page.evaluate("getComputedStyle(document.getElementById('evidence-drawer')).display") == "none"
    assert await page.locator("#focus-exit-button").count() == 0
    await page.locator("#map-focus-button").click()
    await page.wait_for_timeout(200)
    assert await page.locator("#map-focus-button").filter(has_text="Exit map focus").is_visible()
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(200)
    assert await page.locator("#focus-exit-button").count() == 0
    await page.locator("#btn-live").click()
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'LIVE'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    assert await page.locator("#nws-source-line").is_visible()
    await page.close()


async def verify_nws_mode_specificity(browser, seed, live):
    router = Router(seed, live)
    page = await open_ready(browser, (1440, 900), router)
    banner = page.locator("#nws-forecast-banner")
    text = await banner.inner_text()
    assert "HISTORICAL NWS · REPLAY · NOT USED TO RANK" in text, text
    assert "Station: KPHX" in text, text
    assert "NWS FORECAST" not in text
    assert (await page.locator("#hero-context-label").inner_text()).strip() == "HISTORICAL OBSERVATION"

    await page.locator("#btn-live").click()
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'LIVE'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    text = await banner.inner_text()
    assert await banner.is_visible()
    assert "NWS FORECAST · SUPPLEMENTAL · NOT USED TO RANK" in text, text
    assert "40.0°C · Mostly sunny" in text, text
    assert "This Afternoon" in text, text
    assert "not a station observation" in text, text
    assert "HISTORICAL NWS" not in text
    assert (await page.locator("#hero-context-label").inner_text()).strip() == "NWS FORECAST"
    assert await page.locator("#nws-source-line").is_visible()
    assert "candidate 1 leads" in (await page.locator("#ranking-callout").inner_text()).lower()
    assert "Start with candidate 1." in await page.locator("#answer-hero").inner_text()
    assert "DESK READOUT · LIVE" in await page.locator("#status-region").inner_text()
    ranks = await page.locator(".candidate-card").evaluate_all("els => els.map(e => e.dataset.rank)")
    assert ranks == ["1", "2", "3"], ranks

    router.delay_mode = "replay"
    await page.locator("#btn-replay").click()
    await page.wait_for_timeout(250)
    assert await banner.is_hidden()
    assert await banner.get_attribute("hidden") is not None
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'REPLAY'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    text = await banner.inner_text()
    assert "HISTORICAL NWS · REPLAY" in text, text
    assert "NWS FORECAST" not in text
    assert await page.evaluate("getComputedStyle(document.getElementById('nws-source-line')).display") == "none"
    await page.close()

    router = Router(seed, live)
    router.delay_mode = "live"
    page = await open_ready(browser, (1440, 900), router)
    await page.locator("#btn-live").click()
    await page.wait_for_timeout(250)
    assert await page.locator("#nws-forecast-banner").is_hidden()
    await page.wait_for_function("document.querySelector('#mode-badge').textContent.trim() === 'LIVE'", timeout=20000)
    await page.wait_for_selector(".candidate-card[data-rank='1']", timeout=20000)
    assert await page.locator("#nws-forecast-banner").is_visible()
    assert "NWS FORECAST" in await page.locator("#nws-forecast-banner").inner_text()
    await page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        seed_page = await browser.new_page()
        seed = await (await seed_page.request.get(f"{URL}api/answer?mode=replay")).json()
        await seed_page.close()

        for label, intersection, expected in (
            ("success", {"available": True, "name": "MONROE ST & 7TH ST", "distance_m": 104, "used_in_decision": False}, "Nearest intersection: MONROE ST & 7TH ST"),
            ("no-result", {"available": False, "error": "no_intersection_within_200m", "used_in_decision": False}, "No mapped intersection within 200 m"),
            ("provider-failure", {"available": False, "error": "intersection_query_failed: timeout", "used_in_decision": False}, "Location context unavailable"),
        ):
            candidate_payload = json.loads(json.dumps(seed))
            for candidate in candidate_payload["ranked_candidates"]:
                candidate.setdefault("candidate_context", {})["intersection"] = intersection
            router = Router(candidate_payload, candidate_payload)
            page = await open_ready(browser, (1440, 900), router)
            cards = await page.locator(".candidate-card").all_inner_texts()
            assert all(expected in card for card in cards), (label, cards)
            if label != "success":
                assert intersection["available"] is False
                assert all(c["candidate_context"]["intersection"]["available"] is False for c in candidate_payload["ranked_candidates"])
            assert all("used_in_decision" not in card for card in cards)
            ranks = await page.locator(".candidate-card").evaluate_all("els => els.map(e => e.dataset.rank)")
            assert ranks == ["1", "2", "3"], (label, ranks)
            await page.close()

        live = make_live(seed)
        router = Router(seed, live)
        page = await open_ready(browser, (1440, 900), router)
        await verify_explore_click(page)
        await verify_explore_manual(page)
        await verify_highlight(page, seed)
        await page.close()

        router = Router(seed, live, fail_live=True)
        page = await open_ready(browser, (390, 844), router)
        await page.locator("#btn-live").click()
        await page.wait_for_timeout(700)
        assert "UNAVAILABLE" in await page.locator("#status-region").inner_text()
        assert await page.locator("#status-region .mode-button").inner_text() == "Try Replay"
        assert await page.locator("#map").evaluate("el => getComputedStyle(el).minHeight") == "260px"
        await page.close()

        router = Router(seed, live)
        await verify_mobile_stacking(browser, seed, live)
        await verify_hidden_contract(browser, seed, live)
        await verify_nws_mode_specificity(browser, seed, live)

        await browser.close()
        print("LUNA_INTEGRITY_BROWSER: PASS")


if __name__ == "__main__":
    asyncio.run(main())