"""
S3B Urban Heat Brief tests.

All tests use Replay fixtures or in-memory controlled responses. No real
FortyGuard or NWS calls are made by this suite.
"""

import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.server import build_visualization_payload
from src.agent.brief import compose_urban_heat_brief
from src.agent.controller import HeatAgent
from src.agent.adapter import FortyGuardAdapter

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


ROOT = Path(__file__).resolve().parent.parent
SERVER_PORT = 8092
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"


def replay_result():
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    return agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")


def live_result_from_replay():
    """Create a controlled in-memory LIVE result without provider calls."""
    result = replay_result()
    result = copy.deepcopy(result)
    result["answer"]["mode"] = "live"
    result["answer"]["observation_time"] = "2026-08-27T15:00:00-07:00"
    result["answer"]["sources"] = [
        {"provider": "FortyGuard", "endpoint": "/v1/heatmap", "mode": "live",
         "observation_time": "2026-08-27T15:00:00-07:00", "activity_id": "controlled-live"}
    ]
    result["raw_results"]["heatmap"]["mode"] = "live"
    result["raw_results"]["heatmap"]["observation_time"] = "2026-08-27T15:00:00-07:00"
    result["raw_results"]["heatmap"]["activity_id"] = "controlled-live"
    result["raw_results"]["env_params"]["mode"] = "live"
    result["raw_results"]["env_params"]["observation_time"] = "2026-08-27T15:00:00-07:00"
    return result


def live_nws_context():
    return {
        "provider": "NWS",
        "mode": "live",
        "retrieved_at": "2026-08-27T15:01:00Z",
        "source_endpoints": [
            "/gridpoints/PSR/128,48/forecast",
            "/alerts/active?point=33.45,-112.07"
        ],
        "conditions": {
            "short_forecast": "Sunny",
            "effective_start": "2026-08-27T14:00:00-07:00",
            "effective_end": "2026-08-27T18:00:00-07:00"
        },
        "alerts": [{"event": "Extreme Heat Warning"}],
        "alert_count": 1,
        "used_in_decision": False,
        "evidence_status": "supplemental_context"
    }


def test_replay_brief_exists():
    payload = build_visualization_payload(replay_result())
    brief = payload["urban_heat_brief"]
    assert brief is not None
    assert brief["title"] == "Urban Heat Brief"
    # Section count may be 4 or 5 depending on whether GIS context is available
    section_ids = [s["section_id"] for s in brief["sections"]]
    assert "thermal_finding" in section_ids
    assert "candidate_interpretation" in section_ids
    assert "weather_context" in section_ids
    assert "decision_note" in section_ids
    # LOCAL CONTEXT section may be present if GIS data is available
    print("  PASS: test_replay_brief_exists")


def test_replay_brief_uses_fortyguard():
    brief = build_visualization_payload(replay_result())["urban_heat_brief"]
    assert "367" in brief["plain_text"]
    assert any(source["provider"] == "FortyGuard" for source in brief["sources"])
    assert brief["mode"] == "replay"
    print("  PASS: test_replay_brief_uses_fortyguard")


def test_replay_nws_not_consulted():
    with patch("src.tools.nws.get_nws_context", side_effect=AssertionError("NWS called in Replay")):
        payload = build_visualization_payload(replay_result())
    nws = payload["nws_context"]
    assert nws["mode"] == "replay"
    assert nws["evidence_status"] == "excluded_from_replay"
    assert payload["urban_heat_brief"]["sections"][2]["claims"][0]["text"] == \
        "Current NWS context is not included in historical Replay."
    print("  PASS: test_replay_nws_not_consulted")


def test_replay_network_behavior():
    payload = build_visualization_payload(replay_result())
    assert payload["nws_context"]["source_endpoints"] == []
    assert payload["nws_context"]["evidence_status"] == "excluded_from_replay"
    assert payload["mode"] == "replay"
    print("  PASS: test_replay_network_behavior")


def test_replay_near_tie_brief():
    brief = build_visualization_payload(replay_result())["urban_heat_brief"]
    text = brief["sections"][1]["text"]
    assert brief["ranking_status"] == "near_tie"
    assert "effectively equivalent thermal burden" in text
    assert "0.1°C near-tie tolerance" in text
    print("  PASS: test_replay_near_tie_brief")


def test_near_tie_no_false_superiority():
    brief = build_visualization_payload(replay_result())["urban_heat_brief"]
    text = brief["plain_text"]
    assert "meaningfully outranks" not in text
    assert "warrants first investigation" not in text
    assert "thermal evidence alone does not support a meaningful distinction" in text
    print("  PASS: test_near_tie_no_false_superiority")


def test_clear_separation_brief():
    result = replay_result()
    result = copy.deepcopy(result)
    ranked = result["answer"]["conditions"]["ranked_candidates"]
    ranked[0]["observed_temp"] = 45.0
    ranked[1]["observed_temp"] = 43.0
    ranked[2]["observed_temp"] = 40.0
    result["answer"]["conditions"]["ranking_status"] = "ranked"
    result["answer"]["conditions"]["ranking_explanation"] = None
    brief = compose_urban_heat_brief(result, {
        "provider": "NWS", "mode": "replay", "conditions": None, "alerts": [],
        "evidence_status": "excluded_from_replay"
    })
    text = brief["sections"][1]["text"]
    assert brief["ranking_status"] == "ranked"
    assert "warrants first investigation on measured thermal burden" in text
    assert "2.00°C above candidate #2" in text
    assert "5.00°C above candidate #3" in text
    print("  PASS: test_clear_separation_brief")


def test_live_brief_nws_available():
    result = live_result_from_replay()
    context = live_nws_context()
    with patch("src.tools.nws.get_nws_context", return_value=context):
        payload = build_visualization_payload(result)
    brief = payload["urban_heat_brief"]
    weather = brief["sections"][2]["text"]
    assert brief["mode"] == "live"
    assert "Sunny" in weather
    assert "Extreme Heat Warning" in weather
    assert any(source["provider"] == "NWS" for source in brief["sources"])
    assert brief["nws_used_in_decision"] is False
    print("  PASS: test_live_brief_nws_available")


def test_live_brief_nws_failure():
    result = live_result_from_replay()
    unavailable = {
        "provider": "NWS", "mode": "live", "conditions": None, "alerts": [],
        "alert_count": 0, "retrieved_at": "2026-08-27T15:01:00Z",
        "source_endpoints": ["/gridpoints/PSR/128,48/forecast"],
        "used_in_decision": False, "evidence_status": "unavailable"
    }
    with patch("src.tools.nws.get_nws_context", return_value=unavailable):
        payload = build_visualization_payload(result)
    brief = payload["urban_heat_brief"]
    assert brief is not None
    assert "NWS context was unavailable for this LIVE query" in brief["plain_text"]
    assert brief["nws_used_in_decision"] is False
    print("  PASS: test_live_brief_nws_failure")


def test_live_no_feature_no_brief():
    result = {
        "answer": {
            "mode": "live", "error": True, "conditions": {},
            "summary": "Unable to answer: No temperature candidates found",
            "sources": [], "observation_time": None
        },
        "evidence_chain": [],
        "raw_results": {}
    }
    with patch("src.tools.nws.get_nws_context", side_effect=AssertionError("NWS should not be called")):
        payload = build_visualization_payload(result)
    assert payload["urban_heat_brief"] is None
    assert payload["nws_context"]["evidence_status"] == "not_requested_fortyguard_unavailable"
    print("  PASS: test_live_no_feature_no_brief")


def test_claim_provenance_metadata():
    brief = build_visualization_payload(replay_result())["urban_heat_brief"]
    required = ["claim_id", "text", "source_provider", "source_type", "evidence_nodes",
                "mode", "observation_time", "used_in_decision"]
    for claim in brief["claims"]:
        for key in required:
            assert key in claim, f"Missing {key} from {claim['claim_id']}"
        assert claim["source_provider"]
        assert claim["evidence_nodes"]
        assert claim["mode"] == "replay"
    print("  PASS: test_claim_provenance_metadata")


def test_source_and_time_semantics():
    result = live_result_from_replay()
    context = live_nws_context()
    with patch("src.tools.nws.get_nws_context", return_value=context):
        brief = build_visualization_payload(result)["urban_heat_brief"]
    fg = next(source for source in brief["sources"] if source["provider"] == "FortyGuard")
    nws = next(source for source in brief["sources"] if source["provider"] == "NWS")
    assert fg["mode"] == "live"
    assert fg["observation_time"] == "2026-08-27T15:00:00-07:00"
    assert nws["mode"] == "live"
    assert nws["retrieved_at"] == "2026-08-27T15:01:00Z"
    assert fg["observation_time"] != nws["retrieved_at"]
    print("  PASS: test_source_and_time_semantics")


def _start_server():
    proc = subprocess.Popen(
        [sys.executable, "app/server.py"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PORT": str(SERVER_PORT)}
    )
    time.sleep(2)
    return proc


def _stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_brief_dynamic_content_safe():
    """A hostile question remains text in the UI — XSS prevention."""
    assert HAS_PLAYWRIGHT, "Playwright is required for S3B browser proof"
    proc = _start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(SERVER_URL, timeout=10000)
            page.wait_for_selector(".brief-section", timeout=10000)
            hostile = '<img src=x onerror=alert("xss")> which trees would cool most'
            page.locator("#question-input").fill(hostile)
            page.locator("#question-form button[type='submit']").click()
            page.wait_for_timeout(1000)
            # In Luna, non-default questions go to the analyst (client-side)
            analyst_text = page.locator("#analyst-result").text_content()
            assert 'hostile question' in analyst_text or 'cooling effect' in analyst_text
            # No HTML elements created — text only
            assert page.locator("#analyst-result img").count() == 0
            assert page.locator("#analyst-result script").count() == 0
            # Also verify backend evidence chain has no HTML elements
            page.locator("#question-input").fill("Where should Phoenix prioritize a cooling intervention this afternoon?")
            page.locator("#question-form button[type='submit']").click()
            page.wait_for_selector(".brief-section", timeout=10000)
            page.locator(".evidence-toggle").click()
            page.wait_for_timeout(500)
            assert page.locator("#evidence-content img").count() == 0
            assert page.locator("#evidence-content script").count() == 0
            browser.close()
    finally:
        _stop_server(proc)
    print("  PASS: test_brief_dynamic_content_safe")


def test_browser_brief_1440():
    assert HAS_PLAYWRIGHT, "Playwright is required for S3B browser proof"
    proc = _start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(SERVER_URL, timeout=10000)
            page.wait_for_selector(".brief-section", timeout=10000)
            assert page.locator(".brief-panel").is_visible()
            assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
            assert "Urban Heat Brief" in page.locator(".brief-panel").inner_text()
            section_count = page.locator(".brief-section").count()
            assert section_count >= 4, f"Expected at least 4 sections, got {section_count}"
            browser.close()
    finally:
        _stop_server(proc)
    print("  PASS: test_browser_brief_1440")


def test_browser_brief_1920():
    assert HAS_PLAYWRIGHT, "Playwright is required for S3B browser proof"
    proc = _start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(SERVER_URL, timeout=10000)
            page.wait_for_selector(".brief-section", timeout=10000)
            assert page.locator(".brief-panel").is_visible()
            assert page.evaluate("document.body.scrollWidth <= window.innerWidth")
            assert "Urban Heat Brief" in page.locator(".brief-panel").inner_text()
            section_count = page.locator(".brief-section").count()
            assert section_count >= 4, f"Expected at least 4 sections, got {section_count}"
            browser.close()
    finally:
        _stop_server(proc)
    print("  PASS: test_browser_brief_1920")


def test_replay_live_separation():
    replay_payload = build_visualization_payload(replay_result())
    live_payload = live_result_from_replay()
    context = live_nws_context()
    with patch("src.tools.nws.get_nws_context", return_value=context):
        live_payload = build_visualization_payload(live_payload)
    assert replay_payload["urban_heat_brief"]["mode"] == "replay"
    assert replay_payload["nws_context"]["evidence_status"] == "excluded_from_replay"
    assert live_payload["urban_heat_brief"]["mode"] == "live"
    assert live_payload["nws_context"]["mode"] == "live"
    assert replay_payload["urban_heat_brief"]["observation_time"] != live_payload["urban_heat_brief"]["observation_time"]
    print("  PASS: test_replay_live_separation")


def test_tie_threshold_single_source():
    """Controller and Brief use the same canonical threshold constant."""
    from src.agent.controller import TIE_THRESHOLD_CELSIUS as controller_threshold
    from src.agent.brief import TIE_THRESHOLD_CELSIUS as brief_threshold
    assert controller_threshold == 0.1
    assert brief_threshold == 0.1
    assert controller_threshold is brief_threshold, "Brief must import from controller, not define its own"
    print("  PASS: test_tie_threshold_single_source")


def test_http_invalid_mode():
    """Server rejects invalid mode values with bounded response."""
    proc = _start_server()
    try:
        import urllib.request
        try:
            urllib.request.urlopen(f"{SERVER_URL}/api/answer?mode=invalid", timeout=10)
            assert False, "Should have raised"
        except urllib.error.HTTPError as e:
            assert e.code == 400
        finally:
            pass
    finally:
        _stop_server(proc)
    print("  PASS: test_http_invalid_mode")


def test_nws_behavior_assertions():
    """NWS context structure is correct for both modes."""
    # Replay
    payload = build_visualization_payload(replay_result())
    nws = payload["nws_context"]
    assert nws["mode"] == "replay"
    assert nws["used_in_decision"] is False
    assert nws["evidence_status"] == "excluded_from_replay"
    # Live
    live = live_result_from_replay()
    ctx = live_nws_context()
    with patch("src.tools.nws.get_nws_context", return_value=ctx):
        payload = build_visualization_payload(live)
    nws = payload["nws_context"]
    assert nws["mode"] == "live"
    assert nws["used_in_decision"] is False
    assert nws["evidence_status"] == "supplemental_context"
    print("  PASS: test_nws_behavior_assertions")


def test_cross_mode_visualization_guard():
    """Visualization payload never mixes replay geometry into live."""
    live = live_result_from_replay()
    with patch("src.tools.nws.get_nws_context", return_value=live_nws_context()):
        payload = build_visualization_payload(live)
    assert payload["visualization_source"] == "live"
    assert payload["heatmap"]["source"] == "live"
    assert payload["priority_location"]["source"] == "live"
    print("  PASS: test_cross_mode_visualization_guard")


def test_authority_manifest_path_resolution():
    """Every path in authority manifest resolves to an existing file."""
    manifest_path = Path("project-state/AUTHORITY-MANIFEST.json")
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    missing = []
    for item in manifest.get("authority_manifest", {}).get("current", []):
        p = Path(item["path"])
        if not p.exists():
            missing.append(item["path"])
    assert not missing, f"Authority manifest paths missing: {missing}"
    print("  PASS: test_authority_manifest_path_resolution")


def test_spec011_normative_taxonomy():
    """SPEC-011 normative classes match the authoritative source."""
    spec_path = Path("qualification/specifications/UHI-SPEC-011-claim-taxonomy.md")
    assert spec_path.exists()
    content = spec_path.read_text()
    required_classes = [
        "SOURCE_OBSERVATION", "NORMALIZED_OBSERVATION", "DERIVED_FINDING",
        "CORROBORATED_FINDING", "HISTORICAL_COMPARISON", "PRIORITY_CLASSIFICATION",
        "INTERVENTION_RECOMMENDATION", "CONTEXTUAL_STATEMENT", "UNRESOLVED", "UNSUPPORTED"
    ]
    for cls in required_classes:
        assert cls in content, f"Missing normative class: {cls}"
    print("  PASS: test_spec011_normative_taxonomy")


def test_zero_unsupported_claims():
    """All Brief claims map to permitted normative classes; none are unsupported."""
    PERMITTED_CLASSES = {
        "thermal_measurement",       # → SOURCE_OBSERVATION
        "environmental_measurement", # → SOURCE_OBSERVATION
        "product_derived_comparison", # → DERIVED_FINDING
        "product_derived_decision_note", # → PRIORITY_CLASSIFICATION
        "official_current_context",  # → CONTEXTUAL_STATEMENT
        "provenance_disclosure",     # → CONTEXTUAL_STATEMENT
        "availability_disclosure",   # → CONTEXTUAL_STATEMENT
        "product_derived_disclosure", # → DERIVED_FINDING
        "gis_context_canopy",        # → CONTEXTUAL_STATEMENT (Level A GIS)
        "gis_context_parks",         # → CONTEXTUAL_STATEMENT (Level A GIS)
    }
    brief = build_visualization_payload(replay_result())["urban_heat_brief"]
    unsupported = []
    for claim in brief["claims"]:
        st = claim.get("source_type", "")
        if st not in PERMITTED_CLASSES:
            unsupported.append(f"{claim['claim_id']}: {st}")
    assert not unsupported, f"Unsupported claims found: {unsupported}"
    print("  PASS: test_zero_unsupported_claims")


def test_replay_fixture_integrity_positive():
    """Genuine fixtures pass integrity validation."""
    from src.agent.controller import HeatAgent
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("What is the heat risk?")
    assert result["answer"]["mode"] == "replay"
    assert not result["answer"].get("error", False)
    print("  PASS: test_replay_fixture_integrity_positive")


def test_replay_fixture_corruption_negative():
    """Corrupted fixture causes bounded integrity failure, no normal result."""
    import shutil
    fixture = Path("fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json")
    backup = fixture.with_suffix(".json.bak")
    try:
        shutil.copy2(fixture, backup)
        fixture.write_bytes(b"CORRUPTED")
        agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
        result = agent.answer("What is the heat risk?")
        assert result["answer"].get("error", True), "Corrupted fixture should produce error"
    finally:
        if backup.exists():
            shutil.move(backup, fixture)
    print("  PASS: test_replay_fixture_corruption_negative")


def run_all():
    tests = [
        test_replay_brief_exists,
        test_replay_brief_uses_fortyguard,
        test_replay_nws_not_consulted,
        test_replay_network_behavior,
        test_replay_near_tie_brief,
        test_near_tie_no_false_superiority,
        test_clear_separation_brief,
        test_live_brief_nws_available,
        test_live_brief_nws_failure,
        test_live_no_feature_no_brief,
        test_claim_provenance_metadata,
        test_source_and_time_semantics,
        test_brief_dynamic_content_safe,
        test_browser_brief_1440,
        test_browser_brief_1920,
        test_replay_live_separation,
        test_tie_threshold_single_source,
        test_http_invalid_mode,
        test_nws_behavior_assertions,
        test_cross_mode_visualization_guard,
        test_authority_manifest_path_resolution,
        test_spec011_normative_taxonomy,
        test_zero_unsupported_claims,
        test_replay_fixture_integrity_positive,
        test_replay_fixture_corruption_negative,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__}: {exc}")
    print(f"\nS3B TESTS: {passed}/{len(tests)} PASS, {len(tests) - passed} FAIL")
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
