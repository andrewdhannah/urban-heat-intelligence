"""Runtime consumer checks for the R6-R2 integrity pass.

Run with a Luna preview server:
  LUNA_URL=http://127.0.0.1:8091/ python3 tests/test_dashboard_luna_integrity_browser.py
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = os.environ.get("LUNA_URL", "http://127.0.0.1:8090/")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        seed = await browser.new_page(viewport={"width": 1440, "height": 900})
        response = await seed.request.get(f"{URL}api/answer?mode=replay")
        payload = await response.json()
        await seed.close()

        for label, intersection, expected in (
            ("success", {"available": True, "name": "MONROE ST & 7TH ST", "distance_m": 104, "used_in_decision": False}, "Nearest intersection: MONROE ST & 7TH ST"),
            ("no-result", {"available": False, "error": "no_intersection_within_200m", "used_in_decision": False}, "No mapped intersection within 200 m"),
            ("provider-failure", {"available": False, "error": "intersection_query_failed: timeout", "used_in_decision": False}, "Location context unavailable"),
        ):
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            candidate_payload = json.loads(json.dumps(payload))
            for candidate in candidate_payload["ranked_candidates"]:
                candidate.setdefault("candidate_context", {})["intersection"] = intersection

            async def fulfill(route):
                await route.fulfill(status=200, content_type="application/json", body=json.dumps(candidate_payload))

            await page.route("**/api/answer*", fulfill)
            await page.goto(URL, wait_until="networkidle", timeout=120000)
            await page.wait_for_timeout(500)
            cards = await page.locator(".candidate-card").all_inner_texts()
            assert all(expected in card for card in cards), f"{label}: {cards}"
            if label != "success":
                assert intersection["available"] is False
                assert all(candidate["candidate_context"]["intersection"]["available"] is False for candidate in candidate_payload["ranked_candidates"])
            assert all("used_in_decision" not in card for card in cards)
            ranks = await page.locator(".candidate-card").evaluate_all("els => els.map(e => e.dataset.rank)")
            assert ranks == ["1", "2", "3"], f"{label}: rank order {ranks}"
            await page.close()

        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        live_payload = json.loads(json.dumps(payload))
        live_payload["mode"] = "live"
        live_payload["nws_context"] = {"evidence_status": "supplemental_context", "conditions": {"temperature_f": 104, "short_forecast": "Hot"}, "alerts": [], "used_in_decision": False}

        async def live_success(route):
            await route.fulfill(status=200, content_type="application/json", body=json.dumps(live_payload))

        await page.route("**/api/answer*", live_success)
        await page.goto(URL, wait_until="networkidle", timeout=120000)
        await page.locator("#btn-live").click()
        await page.wait_for_timeout(500)
        assert await page.locator("#mode-badge").inner_text() == "LIVE"
        assert "DESK READOUT · LIVE" in await page.locator("#status-region").inner_text()
        assert live_payload["mode"] == "live"
        assert "NWS FORECAST" in await page.locator("#nws-forecast-banner").inner_text()
        assert await page.locator(".candidate-card").count() == 3
        await page.close()

        page = await browser.new_page(viewport={"width": 390, "height": 844})

        async def live_failure(route):
            await route.fulfill(status=500, content_type="application/json", body=json.dumps({"error": True, "mode": "live", "message": "mock failure"}))

        await page.route("**/api/answer*", live_failure)
        await page.goto(URL, wait_until="networkidle", timeout=120000)
        await page.locator("#btn-live").click()
        await page.wait_for_timeout(500)
        assert "UNAVAILABLE" in await page.locator("#status-region").inner_text()
        assert await page.locator("#status-region .mode-button").inner_text() == "Try Replay"
        assert await page.locator("#map").evaluate("el => getComputedStyle(el).minHeight") == "260px"
        await browser.close()
        print("LUNA_INTEGRITY_BROWSER: PASS")


if __name__ == "__main__":
    asyncio.run(main())
