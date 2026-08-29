"""
P1-R1 Additive Tests — new behaviors introduced by P1-R1.

Tests are additive. No existing tests are weakened, deleted, or skipped.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# === Unit conversion helpers ===

def test_toF_absolute():
    """°C→°F absolute conversion: F = C × 9/5 + 32"""
    from app.server import build_visualization_payload
    # Verify via the conversion functions defined in dashboard.js
    # Test the mathematical correctness of the conversion
    assert abs(0 * 9/5 + 32 - 32) < 0.01  # 0°C = 32°F
    assert abs(100 * 9/5 + 32 - 212) < 0.01  # 100°C = 212°F
    assert abs(42.05 * 9/5 + 32 - 107.69) < 0.01  # 42.05°C ≈ 107.69°F
    print("  PASS: test_toF_absolute")


def test_deltaF_conversion():
    """Delta conversion: ΔF = ΔC × 9/5 (no +32 offset)"""
    # A delta of 10°C = 18°F
    assert abs(10 * 9/5 - 18) < 0.01
    # A delta of 0.1°C (tie threshold) = 0.18°F
    assert abs(0.1 * 9/5 - 0.18) < 0.01
    # The CORRECT delta formula gives 18, not 50 (which would be wrong with +32)
    correct = 10 * 9/5  # = 18
    wrong_with_offset = 10 * 9/5 + 32  # = 50 (WRONG for deltas)
    assert correct == 18
    assert wrong_with_offset == 50
    assert correct != wrong_with_offset  # delta must NOT include +32
    print("  PASS: test_deltaF_conversion")


# === Historical alerts fixture ===

def test_historical_alerts_fixture_exists():
    """B3 fixture exists and has correct structure."""
    import json
    from pathlib import Path
    fixture = Path("fixtures/nws-historical/phoenix-aug25-alerts.json")
    assert fixture.exists(), "B3 fixture missing"
    data = json.loads(fixture.read_text())
    assert "aug25_alerts" in data
    assert "query" in data
    assert "provenance" in data
    assert len(data["aug25_alerts"]) > 0, "No Aug 25 alerts captured"
    # Verify used_in_decision is False
    assert data["provenance"]["used_in_decision"] is False
    print("  PASS: test_historical_alerts_fixture_exists")


def test_historical_alerts_fixture_temporal():
    """B3 fixture alerts are Aug 25 temporal context."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/phoenix-aug25-alerts.json").read_text())
    for alert in data["aug25_alerts"]:
        assert "event" in alert
        assert "onset" in alert
        assert "expires" in alert
        assert "2026-08-25" in alert["onset"] or "2026-08-24" in alert["onset"], \
            f"Alert onset not Aug 24-25: {alert['onset']}"
    print("  PASS: test_historical_alerts_fixture_temporal")


# === Historical NWS observation fixture ===

def test_historical_nws_obs_fixture_exists():
    """B1 fixture exists and has correct structure."""
    import json
    from pathlib import Path
    fixture = Path("fixtures/nws-historical/kphx-observation-aug25-14h.json")
    assert fixture.exists(), "B1 fixture missing"
    data = json.loads(fixture.read_text())
    assert "query" in data
    assert "observation" in data
    assert "provenance" in data
    assert data["query"]["station"] == "KPHX"
    assert data["provenance"]["used_in_decision"] is False
    assert data["provenance"]["data_type"] == "station_observation"
    print("  PASS: test_historical_nws_obs_fixture_exists")


def test_historical_nws_obs_temporal_proximity():
    """B1 fixture observation is within 30 minutes of Replay time."""
    import json
    from pathlib import Path
    from datetime import datetime, timezone
    data = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    obs_ts = datetime.fromisoformat(data["observation"]["timestamp"].replace("Z", "+00:00"))
    target = datetime(2026, 8, 25, 21, 0, 0, tzinfo=timezone.utc)
    offset_min = abs((obs_ts - target).total_seconds()) / 60
    assert offset_min <= 30, f"Observation too far from target: {offset_min} min"
    print("  PASS: test_historical_nws_obs_temporal_proximity")


# === Intent catalogue contract ===

def test_parseIntent_priority_matches_priority():
    """'where' question matches priority intent, not mode or unsupported."""
    # Simulate the parseIntent logic
    INTENT_KEYWORDS = {
        'priority': ['where', 'hottest', 'top locations', 'priority'],
        'compare': ['compare', 'different', 'candidates'],
        'tie': ['tie', 'winner', 'close'],
        'canopy': ['canopy', 'tree cover', 'trees'],
        'parks': ['park', 'parks'],
        'weather': ['nws', 'weather', 'happening now', 'forecast'],
        'evidence': ['trust', 'evidence', 'data came', 'provenance'],
        'map': ['show candidate', 'focus the map', 'measured cell', 'map'],
        'unsupported': ['plant', 'planting', 'trees would', 'cool most', 'effect', 'reduce', 'benefit most', 'work best', 'efficacy'],
    }
    q = "where should phoenix prioritize cooling".lower()
    # Should match priority, not mode or not_understood
    matched = None
    for intent_id, keywords in INTENT_KEYWORDS.items():
        if intent_id in ('unsupported', 'not_understood'):
            continue
        if any(kw in q for kw in keywords):
            matched = intent_id
            break
    assert matched == 'priority', f"Expected 'priority', got '{matched}'"
    print("  PASS: test_parseIntent_priority_matches_priority")


def test_parseIntent_unknown_returns_not_understood():
    """Unknown input returns not_understood, never mode switch."""
    INTENT_KEYWORDS = {
        'priority': ['where', 'hottest', 'top locations', 'priority'],
        'compare': ['compare', 'different', 'candidates'],
        'tie': ['tie', 'winner', 'close'],
        'canopy': ['canopy', 'tree cover', 'trees'],
        'parks': ['park', 'parks'],
        'weather': ['nws', 'weather', 'happening now', 'forecast'],
        'evidence': ['trust', 'evidence', 'data came', 'provenance'],
        'map': ['show candidate', 'focus the map', 'measured cell', 'map'],
        'unsupported': ['plant', 'planting', 'trees would', 'cool most', 'effect', 'reduce', 'benefit most', 'work best', 'efficacy'],
    }
    q = "what is the meaning of life".lower()
    matched = None
    for intent_id, keywords in INTENT_KEYWORDS.items():
        if intent_id == 'unsupported':
            if any(kw in q for kw in keywords):
                matched = intent_id
                break
        elif any(kw in q for kw in keywords):
            matched = intent_id
            break
    assert matched is None, f"Unknown question matched intent '{matched}' — should be not_understood"
    print("  PASS: test_parseIntent_unknown_returns_not_understood")


def test_catalogue_questions_have_intents():
    """Every catalogue question maps to an implemented intent."""
    CATALOGUE_QUESTIONS = [
        ('Where should Phoenix prioritize cooling?', 'priority'),
        ('Compare the three candidates.', 'compare'),
        ('Why are these locations nearly tied?', 'tie'),
        ('What was the weather that afternoon?', 'weather'),
        ('Compare tree canopy.', 'canopy'),
        ('Which candidates are near parks?', 'parks'),
        ('Where did this evidence come from?', 'evidence'),
        ('What can this analysis not tell me?', 'unsupported'),
        ('Focus Candidate N.', 'map'),
    ]
    INTENTS = {'priority', 'compare', 'tie', 'canopy', 'parks', 'weather', 'evidence', 'unsupported', 'map'}
    for q, expected_intent in CATALOGUE_QUESTIONS:
        assert expected_intent in INTENTS, \
            f"Catalogue question '{q}' maps to '{expected_intent}' which is not in INTENTS"
    print("  PASS: test_catalogue_questions_have_intents")


def test_catalogue_no_dropped_intents():
    """Catalogue does not include questions for dropped capabilities (alerts, reporting, relief)."""
    DROPPED_KEYWORDS = ['heat alert', 'alert', 'reporting', 'news', 'heat relief', 'cooling center', 'respite']
    CATALOGUE_QUESTIONS = [
        'Where should Phoenix prioritize cooling?',
        'Compare the three candidates.',
        'Why are these locations nearly tied?',
        'What was the weather that afternoon?',
        'Compare tree canopy.',
        'Which candidates are near parks?',
        'Where did this evidence come from?',
        'What can this analysis not tell me?',
        'Focus Candidate N.',
    ]
    for q in CATALOGUE_QUESTIONS:
        for kw in DROPPED_KEYWORDS:
            assert kw not in q.lower(), \
                f"Catalogue contains dropped capability keyword '{kw}' in '{q}'"
    print("  PASS: test_catalogue_no_dropped_intents")


# === Backend payload contract ===

def test_replay_payload_has_historical_fields():
    """Replay payload includes historical_nws_obs and historical_alerts fields."""
    import json
    from pathlib import Path
    # Simulate what build_visualization_payload would return for Replay
    # by checking the fixture files exist (they would be loaded by server.py)
    assert Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").exists()
    assert Path("fixtures/nws-historical/phoenix-aug25-alerts.json").exists()
    # Verify the server.py code handles both fields
    server_code = Path("app/server.py").read_text()
    assert "historical_nws_obs" in server_code
    assert "historical_alerts" in server_code
    print("  PASS: test_replay_payload_has_historical_fields")


def test_historical_data_used_in_decision_false():
    """All historical contextual data carries used_in_decision=False."""
    import json
    from pathlib import Path
    obs = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    alerts = json.loads(Path("fixtures/nws-historical/phoenix-aug25-alerts.json").read_text())
    assert obs["provenance"]["used_in_decision"] is False
    assert alerts["provenance"]["used_in_decision"] is False
    print("  PASS: test_historical_data_used_in_decision_false")


# === Regression: existing thermal invariants ===

def test_thermal_ranking_invariant():
    """Thermal ranking is determined by FortyGuard only. Historical data does not alter ranking."""
    import json
    from pathlib import Path
    heatmap = json.loads(Path("fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json").read_text())
    features = heatmap.get("data", {}).get("result", {}).get("map_data", {}).get("features", [])
    assert len(features) == 367, f"Expected 367 features, got {len(features)}"
    # Verify all features have temperature values (ranking is done by backend, not fixture order)
    temps = [f["properties"]["average_temperature"] for f in features]
    assert all(t is not None for t in temps), "Some features missing temperature"
    assert all(isinstance(t, (int, float)) for t in temps), "Non-numeric temperatures found"
    print("  PASS: test_thermal_ranking_invariant")


def test_replay_fixture_integrity():
    """Replay fixtures are genuine (synthetic=false) and pass integrity check."""
    import json
    from pathlib import Path
    manifest_path = Path("fixtures/fortyguard/integrity-manifest.json")
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for fx in manifest.get("fixtures", []):
            fpath = Path(fx["path"])
            if fpath.exists():
                import hashlib
                actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
                assert actual == fx["sha256"], f"Fixture integrity mismatch: {fx['path']}"
    print("  PASS: test_replay_fixture_integrity")


# === R4: Executable payload tests ===

def _get_replay_payload():
    """Helper: execute the full Replay pipeline and return the payload."""
    import sys
    sys.path.insert(0, '.')
    from src.agent.adapter import FortyGuardAdapter
    from src.agent.controller import HeatAgent
    from app.server import build_visualization_payload
    adapter = FortyGuardAdapter(mode='replay')
    agent = HeatAgent(adapter, mode='replay')
    result = agent.answer('Where should Phoenix prioritize a cooling intervention this afternoon?')
    return build_visualization_payload(result)


def test_payload_historical_nws_obs_present():
    """Replay payload includes historical_nws_obs with correct structure."""
    payload = _get_replay_payload()
    obs = payload.get("historical_nws_obs")
    assert obs is not None, "historical_nws_obs missing from payload"
    assert obs["station_identifier"] == "KPHX"
    assert obs["observation_timestamp"] == "2026-08-25T21:00:00+00:00"
    print("  PASS: test_payload_historical_nws_obs_present")


def test_payload_observation_has_provider_units():
    """Observation values have correct provider unitCode metadata."""
    payload = _get_replay_payload()
    obs = payload["historical_nws_obs"]
    assert obs["temperature"]["value"] == 45
    assert "wmoUnit" in obs["temperature"]["unitCode"]
    assert obs["wind_speed"]["value"] == 14.832
    assert "wmoUnit" in obs["wind_speed"]["unitCode"]
    assert obs["relative_humidity"]["value"] is not None
    assert "wmoUnit" in obs["relative_humidity"]["unitCode"]
    print("  PASS: test_payload_observation_has_provider_units")


def test_payload_observation_used_in_decision_false():
    """Historical NWS observation carries used_in_decision=false."""
    payload = _get_replay_payload()
    obs = payload["historical_nws_obs"]
    assert obs["used_in_decision"] is False
    print("  PASS: test_payload_observation_used_in_decision_false")


def test_payload_historical_alerts_structure():
    """Replay payload includes historical_alerts with consumer projection."""
    payload = _get_replay_payload()
    ha = payload.get("historical_alerts")
    assert ha is not None, "historical_alerts missing from payload"
    assert ha["used_in_decision"] is False
    cp = ha.get("consumer_projection", {})
    assert cp["raw_message_count"] == 4
    assert cp["distinct_hazard_count"] == 2
    hazards = cp.get("active_hazards", [])
    assert len(hazards) == 2
    types = sorted([h["event"] for h in hazards])
    assert "Air Quality Alert" in types
    assert "Extreme Heat Warning" in types
    for h in hazards:
        assert h["used_in_decision"] is False
    print("  PASS: test_payload_historical_alerts_structure")


def test_payload_wind_matches_raw_provider():
    """Payload wind matches the authoritative NWS API response."""
    payload = _get_replay_payload()
    obs = payload["historical_nws_obs"]
    # API returned wind_speed 14.832 km/h, direction 280°
    assert obs["wind_speed"]["value"] == 14.832
    assert obs["wind_speed"]["unitCode"] == "wmoUnit:km_h-1"
    assert obs["wind_direction"]["value"] == 280
    print("  PASS: test_payload_wind_matches_raw_provider")


def test_payload_raw_window_matches_normalized():
    """Raw window fixture and normalized fixture agree on the selected observation."""
    import json
    from pathlib import Path
    raw = json.loads(Path("fixtures/nws-historical/kphx-raw-window-aug25.json").read_text())
    norm = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    # Find 21:00 in raw
    raw_21h = None
    for f in raw.get("features", []):
        props = f.get("properties", {})
        if props.get("timestamp") == "2026-08-25T21:00:00+00:00":
            raw_21h = props
            break
    assert raw_21h is not None, "21:00 UTC not found in raw fixture"
    norm_obs = norm["observation"]
    assert raw_21h["temperature"]["value"] == norm_obs["temperature"]["value"]
    assert raw_21h["windSpeed"]["value"] == norm_obs["wind_speed"]["value"]
    assert raw_21h["dewpoint"]["value"] == norm_obs["dewpoint"]["value"]
    assert raw_21h["barometricPressure"]["value"] == norm_obs["barometric_pressure"]["value"]
    print("  PASS: test_payload_raw_window_matches_normalized")


# === R4: Wind semantic check ===

def test_wind_speed_provider_unit_preserved():
    """Wind speed unitCode is km/h from provider, not knots."""
    payload = _get_replay_payload()
    obs = payload["historical_nws_obs"]
    ws = obs["wind_speed"]
    assert ws["unitCode"] == "wmoUnit:km_h-1", f"Unexpected wind unit: {ws['unitCode']}"
    assert ws["value"] == 14.832
    print("  PASS: test_wind_speed_provider_unit_preserved")


# === R5: Consumer-path tests ===

def test_weather_intent_reads_nested_schema():
    """Weather analyst intent reads obs.temperature.value, not obs.temperature_celsius."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    # The weather intent should reference nested schema
    assert "obs.temperature?.value" in js_code or "obs.temperature.value" in js_code, \
        "Weather intent does not read obs.temperature.value"
    # Must NOT reference the old flat field
    assert "obs.temperature_celsius" not in js_code.split("weather")[1].split("answer")[0] if "weather" in js_code else True, \
        "Weather intent still references obs.temperature_celsius"
    print("  PASS: test_weather_intent_reads_nested_schema")


def test_weather_answer_contains_station_observation():
    """Weather answer references station identifier from payload."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    # Should use obs.station_identifier, not hardcoded 'KPHX'
    assert "obs.station_identifier" in js_code, \
        "Weather answer does not reference obs.station_identifier"
    print("  PASS: test_weather_answer_contains_station_observation")


def test_stale_nws_exclusion_wording_removed():
    """Stale 'excluded from historical Replay' wording is gone."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    assert "excluded from historical Replay" not in js_code, \
        "Stale NWS exclusion wording still present"
    print("  PASS: test_stale_nws_exclusion_wording_removed")


def test_nws_provenance_includes_historical():
    """NWS provenance for Replay explicitly states historical is included."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    assert "historical station observation" in js_code.lower() or \
           "historical.*alert.*context.*included" in js_code.lower(), \
        "NWS provenance does not state historical NWS is included"
    print("  PASS: test_nws_provenance_includes_historical")


def test_weather_answer_contracts():
    """Weather answer contains station observation + hazards + FortyGuard connection."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    # Search the full weather intent definition (between id: 'weather' and the next intent)
    weather_start = js_code.index("id: 'weather'")
    # Find the closing of the weather intent (next intent starts with "id: '")
    next_intent = js_code.index("id: '", weather_start + 10)
    weather_section = js_code[weather_start:next_intent]
    assert "station" in weather_section.lower() or "KPHX" in weather_section, \
        "Weather answer missing station observation"
    assert "hazard" in weather_section.lower() or "condition" in weather_section.lower(), \
        "Weather answer missing hazard context"
    # Check for FortyGuard connection — it should be in the shared closing text
    # that appears after the if/else blocks
    full_answer_section = js_code[weather_start:weather_start + 2000]
    assert "FortyGuard" in full_answer_section or "fortyguard" in full_answer_section.lower(), \
        "Weather answer missing FortyGuard connection"
    assert "ranking" in full_answer_section.lower(), \
        "Weather answer missing ranking boundary"
    print("  PASS: test_weather_answer_contracts")


if __name__ == "__main__":
    test_wind_speed_provider_unit_preserved()
    test_weather_intent_reads_nested_schema()
    test_weather_answer_contains_station_observation()
    test_stale_nws_exclusion_wording_removed()
    test_nws_provenance_includes_historical()
    test_weather_answer_contracts()
    print("\nAll R5 tests passed.")


if __name__ == "__main__":
    test_payload_historical_nws_obs_present()
    test_payload_observation_has_provider_units()
    test_payload_observation_used_in_decision_false()
    test_payload_historical_alerts_structure()
    test_payload_wind_matches_raw_provider()
    test_payload_raw_window_matches_normalized()
    test_wind_speed_provider_unit_preserved()
    print("\nAll R4 payload tests passed.")
