"""
S2 Controlled LIVE Visualization Proof

Uses Playwright route interception to mock LIVE API responses.
Real server handles REPLAY. Browser fetch is intercepted for LIVE.
No real FortyGuard API calls.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

SERVER_PORT = 8091
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
CONTROLLED_LIVE_OBS_TIME = "2026-08-26T15:00:00-07:00"

# Controlled LIVE response — structurally valid, clearly distinguishable from replay
CONTROLLED_LIVE_RESPONSE = {
    "mode": "live",
    "visualization_source": "live",
    "observation_time": CONTROLLED_LIVE_OBS_TIME,
    "summary": "Latest available FortyGuard observation for Phoenix, AZ: area experiencing very high thermal conditions.",
    "conditions": {
        "area_mean_temperature_celsius": 43.17,
        "area_max_temperature_celsius": 44.8,
        "area_min_temperature_celsius": 41.5,
        "area_temperature_range_celsius": 3.3,
        "feature_count": 3,
        "representative_location": {
            "heat_index_celsius": 40.1,
            "apparent_temperature_celsius": 47.3,
            "relative_humidity_percent": 12.5,
            "measured_temperature_celsius": 44.8,
        },
        "measured_result": {
            "apparent_vs_measured_delta_celsius": 2.5,
            "interpretation": "Apparent temperature exceeds measured temperature"
        }
    },
    "why_this_answer": "Controlled LIVE test fixture — question asks for intervention prioritization",
    "sources": [{"provider": "FortyGuard", "endpoint": "/v1/heatmap", "mode": "live",
                 "observation_time": CONTROLLED_LIVE_OBS_TIME, "activity_id": "controlled-live-001"}],
    "heatmap": {
        "features": [
            {"id": "live-test-0", "type": "Feature", "properties": {"tile_id": 9000, "average_temperature": 41.5},
             "geometry": {"type": "Polygon", "coordinates": [[
                 [-112.075, 33.450], [-112.070, 33.450],
                 [-112.070, 33.455], [-112.075, 33.455],
                 [-112.075, 33.450]
             ]]}},
            {"id": "live-test-1", "type": "Feature", "properties": {"tile_id": 9001, "average_temperature": 43.2},
             "geometry": {"type": "Polygon", "coordinates": [[
                 [-112.080, 33.455], [-112.075, 33.455],
                 [-112.075, 33.460], [-112.080, 33.460],
                 [-112.080, 33.455]
             ]]}},
            {"id": "live-test-2", "type": "Feature", "properties": {"tile_id": 9002, "average_temperature": 44.8},
             "geometry": {"type": "Polygon", "coordinates": [[
                 [-112.065, 33.445], [-112.060, 33.445],
                 [-112.060, 33.450], [-112.065, 33.450],
                 [-112.065, 33.445]
             ]]}},
        ],
        "observation_time": CONTROLLED_LIVE_OBS_TIME,
        "feature_count": 3,
        "source": "live"
    },
    "priority_location": {
        "coordinate": [-112.065, 33.445],
        "temperature": 44.8,
        "selection_method": "global_maximum_temperature_feature",
        "source": "live",
        "env_params": {"heat_index": 40.1, "apparent_temp": 47.3, "humidity": 12.5}
    },
    "evidence_chain": [
        {"step": "user_request", "data": {"question": "test", "location": "Phoenix, AZ"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "plan", "data": {"interpreted_intent": "cooling_prioritization", "selected_tools": ["get_heatmap", "get_environmental_parameters"]}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "heatmap_request", "data": {"endpoint": "/v1/heatmap", "mode": "live"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "heatmap_result", "data": {"tool": "get_heatmap", "feature_count": 3, "mean_temp": 43.17, "mode": "live"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "coordinate_selection", "data": {"selected_coordinate": {"temperature_celsius": 44.8}, "selection_method": "global_maximum_temperature_feature"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "env_params_request", "data": {"endpoint": "/v1/env_params", "mode": "live"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "env_params_result", "data": {"tool": "get_environmental_parameters", "heat_index": 40.1, "apparent_temp": 47.3, "humidity": 12.5, "mode": "live"}, "timestamp": "2026-08-26T22:00:00Z"},
        {"step": "answer", "data": {"summary": "Controlled test", "mode": "live", "observation_time": CONTROLLED_LIVE_OBS_TIME}, "timestamp": "2026-08-26T22:00:00Z"},
    ],
    "error": False
}


def start_real_server():
    proc = subprocess.Popen(
        [sys.executable, "app/server.py"],
        cwd=str(Path(__file__).resolve().parent.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**__import__('os').environ, "PORT": str(SERVER_PORT)}
    )
    time.sleep(2)
    return proc


def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_controlled_live_test():
    if not HAS_PLAYWRIGHT:
        print("  SKIP: playwright not installed")
        return True

    proc = start_real_server()
    passed = 0
    failed = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})

            # Intercept LIVE API calls — return controlled fixture
            def handle_route(route):
                if "mode=live" in route.request.url:
                    route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps(CONTROLLED_LIVE_RESPONSE)
                    )
                else:
                    route.continue_()

            page.route("**/api/answer*", handle_route)

            # Load page (auto-runs REPLAY via real server)
            page.goto(SERVER_URL, timeout=10000)
            page.wait_for_selector("#answer-hero[style*='block']", timeout=10000)

            # === 01: REPLAY BASELINE ===
            try:
                mode = page.evaluate("currentMode")
                replay_polys = page.evaluate("(function(){var c=0;Object.values(map._layers).forEach(function(l){if(l instanceof L.Polygon)c++});return c;})()")
                assert mode == "replay", f"Expected replay, got {mode}"
                assert replay_polys == 367, f"Expected 367 replay polygons, got {replay_polys}"
                print("  PASS: controlled_01_replay_baseline")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_01_replay_baseline: {e}")
                failed += 1

            # === 02: SWITCH TO LIVE AND EXECUTE (intercepted) ===
            try:
                page.click("#btn-live")
                page.click(".btn-primary")
                page.wait_for_selector("#answer-hero[style*='block']", timeout=15000)
                time.sleep(1)
                print("  PASS: controlled_02_live_switch_and_execute")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_02_live_switch_and_execute: {e}")
                failed += 1

            # === 03: SUCCESSFUL LIVE RESULT ===
            try:
                d = json.loads(page.evaluate("""JSON.stringify({
                    mode: currentData ? currentData.mode : 'none',
                    vis_source: currentData ? currentData.visualization_source : 'none',
                    heat_source: currentData && currentData.heatmap ? currentData.heatmap.source : 'none',
                    feature_count: currentData && currentData.heatmap ? currentData.heatmap.feature_count : 0,
                    obs_time: currentData ? currentData.observation_time : 'none',
                    error: currentData ? currentData.error : true,
                    polygons: (function(){var c=0;Object.values(map._layers).forEach(function(l){if(l instanceof L.Polygon)c++});return c;})(),
                    badge: document.getElementById('mode-badge').textContent
                })"""))

                assert d["mode"] == "live", f"LIVE mode: {d['mode']}"
                assert d["vis_source"] == "live", f"LIVE vis_source: {d['vis_source']}"
                assert d["heat_source"] == "live", f"LIVE heat_source: {d['heat_source']}"
                assert d["feature_count"] == 3, f"LIVE features: {d['feature_count']}"
                assert d["polygons"] > 0, f"LIVE polygons: {d['polygons']}"
                assert not d["error"], f"LIVE error: {d['error']}"
                assert "LIVE" in d["badge"].upper(), f"LIVE badge: {d['badge']}"
                assert CONTROLLED_LIVE_OBS_TIME in d["obs_time"], f"LIVE obs: {d['obs_time']}"

                print(f"  PASS: controlled_03_successful_live (mode={d['mode']}, vis={d['vis_source']}, features={d['feature_count']}, polys={d['polygons']})")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_03_successful_live: {e}")
                failed += 1

            # === 04: LIVE PRIORITY MARKER ===
            try:
                markers = page.evaluate("(function(){var c=0;Object.values(map._layers).forEach(function(l){if(l instanceof L.Marker)c++});return c;})()")
                assert markers >= 1, f"LIVE markers: {markers}"
                print("  PASS: controlled_04_live_priority_marker")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_04_live_priority_marker: {e}")
                failed += 1

            # === 05: NO REPLAY FIXTURE DURING LIVE ===
            try:
                fixture = page.evaluate("currentData && currentData.heatmap && currentData.heatmap.fixture_reference ? true : false")
                assert not fixture, f"Replay fixture used during LIVE: {fixture}"
                print("  PASS: controlled_05_no_replay_fixture_during_live")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_05_no_replay_fixture_during_live: {e}")
                failed += 1

            # === 06: SWITCH BACK TO REPLAY (real server) ===
            try:
                page.click("#btn-replay")
                page.click(".btn-primary")
                page.wait_for_selector("#answer-hero[style*='block']", timeout=10000)
                time.sleep(1)

                d2 = json.loads(page.evaluate("""JSON.stringify({
                    mode: currentData ? currentData.mode : 'none',
                    vis_source: currentData && currentData.heatmap ? currentData.heatmap.source : 'none',
                    feature_count: currentData && currentData.heatmap ? currentData.heatmap.feature_count : 0,
                    polygons: (function(){var c=0;Object.values(map._layers).forEach(function(l){if(l instanceof L.Polygon)c++});return c;})(),
                    obs_time: currentData ? currentData.observation_time : 'none'
                })"""))

                assert d2["mode"] == "replay", f"Return replay mode: {d2['mode']}"
                assert d2["vis_source"] == "replay", f"Return replay vis: {d2['vis_source']}"
                assert d2["feature_count"] == 367, f"Return replay features: {d2['feature_count']}"
                assert d2["polygons"] == 367, f"Return replay polygons: {d2['polygons']}"
                assert "2026-08-25" in d2["obs_time"], f"Return replay obs: {d2['obs_time']}"

                print(f"  PASS: controlled_06_replay_return (features={d2['feature_count']}, polys={d2['polygons']})")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_06_replay_return: {e}")
                failed += 1

            # === 07: GEOMETRY IDENTITY ===
            try:
                # LIVE has tile_ids 9000-9002, REPLAY has tile_ids 0-366
                page.click("#btn-live")
                page.click(".btn-primary")
                page.wait_for_selector("#answer-hero[style*='block']", timeout=15000)
                time.sleep(1)
                live_ids = page.evaluate("currentData.heatmap.features.map(function(f){return f.id||f.properties.tile_id}).sort().join(',')")

                page.click("#btn-replay")
                page.click(".btn-primary")
                page.wait_for_selector("#answer-hero[style*='block']", timeout=10000)
                time.sleep(1)
                replay_id_sample = page.evaluate("currentData.heatmap.features.slice(0,3).map(function(f){return f.id||f.properties.tile_id}).join(',')")

                assert "live-test-0" in live_ids or "9000" in live_ids, f"LIVE test IDs not found: {live_ids}"
                assert live_ids != replay_id_sample, "LIVE and REPLAY geometry identical"
                print(f"  PASS: controlled_07_geometry_identity (LIVE distinct from REPLAY)")
                passed += 1
            except Exception as e:
                print(f"  FAIL: controlled_07_geometry_identity: {e}")
                failed += 1

            browser.close()

    finally:
        stop_server(proc)

    print(f"\nCONTROLLED LIVE TESTS: {passed}/{passed+failed} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_controlled_live_test()
    sys.exit(0 if success else 1)
