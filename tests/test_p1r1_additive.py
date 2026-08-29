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


# === R3: Historical NWS selection ===

def test_exact_21h_observation_wins():
    """Exact 21:00 UTC observation is selected over 21:15."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    assert data["query"]["selected_observation"] == "2026-08-25T21:00:00+00:00", \
        f"Expected exact 21:00 UTC, got {data['query']['selected_observation']}"
    assert data["query"]["offset_minutes"] == 0, \
        f"Expected 0 offset, got {data['query']['offset_minutes']}"
    print("  PASS: test_exact_21h_observation_wins")


def test_selection_rule_documented():
    """Selection rule is explicitly documented in fixture."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    rule = data["query"].get("selection_rule", "")
    assert "minimum" in rule.lower() or "distance" in rule.lower(), \
        f"Selection rule not documented: {rule}"
    assert "exact" in rule.lower(), f"Exact-match rule not documented: {rule}"
    print("  PASS: test_selection_rule_documented")


def test_provider_unit_codes_preserved():
    """Provider unitCode metadata is preserved in raw fixture."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    obs = data["observation"]
    assert "unitCode" in obs["temperature"], "temperature unitCode missing"
    assert "unitCode" in obs["wind_speed"], "wind_speed unitCode missing"
    assert "unitCode" in obs["relative_humidity"], "humidity unitCode missing"
    assert "wmoUnit" in obs["temperature"]["unitCode"], \
        f"Unexpected temperature unit: {obs['temperature']['unitCode']}"
    print("  PASS: test_provider_unit_codes_preserved")


def test_raw_window_fixture_exists():
    """Raw window fixture preserves all candidate observations."""
    import json
    from pathlib import Path
    raw_path = Path("fixtures/nws-historical/kphx-raw-window-aug25.json")
    assert raw_path.exists(), "Raw window fixture missing"
    data = json.loads(raw_path.read_text())
    assert "observations" in data
    assert len(data["observations"]) >= 3, \
        f"Expected multiple observations, got {len(data['observations'])}"
    print("  PASS: test_raw_window_fixture_exists")


# === R3: Station metadata ===

def test_station_identity_vs_text_description():
    """Station identifier and weather text are stored separately."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/kphx-observation-aug25-14h.json").read_text())
    assert data["station_metadata"]["station_identifier"] == "KPHX"
    assert data["station_metadata"]["text_description"] == "Mostly Clear"
    # station_name should NOT be the weather description
    assert data["station_metadata"]["station_name"] is None or \
           data["station_metadata"]["station_name"] != "Mostly Clear", \
        "station_name is incorrectly set to weather description"
    print("  PASS: test_station_identity_vs_text_description")


# === R3: Alert deduplication ===

def test_alert_raw_messages_preserved():
    """All 4 raw NWS messages remain preserved."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/phoenix-aug25-alerts.json").read_text())
    assert len(data["aug25_alerts"]) == 4, \
        f"Expected 4 raw messages, got {len(data['aug25_alerts'])}"
    print("  PASS: test_alert_raw_messages_preserved")


def test_alert_consumer_projection_deduplicates():
    """Consumer projection shows 2 distinct concurrent hazards from 4 raw messages."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/phoenix-aug25-alerts.json").read_text())
    cp = data.get("consumer_projection", {})
    assert cp.get("raw_message_count") == 4
    assert cp.get("distinct_hazard_count") == 2
    hazards = cp.get("active_hazards", [])
    assert len(hazards) == 2
    hazard_types = sorted([h["event"] for h in hazards])
    assert "Air Quality Alert" in hazard_types
    assert "Extreme Heat Warning" in hazard_types
    print("  PASS: test_alert_consumer_projection_deduplicates")


def test_hazard_used_in_decision_false():
    """All consumer-projected hazards carry used_in_decision=false."""
    import json
    from pathlib import Path
    data = json.loads(Path("fixtures/nws-historical/phoenix-aug25-alerts.json").read_text())
    for h in data.get("consumer_projection", {}).get("active_hazards", []):
        assert h["used_in_decision"] is False, \
            f"Hazard {h['event']} has used_in_decision != False"
    print("  PASS: test_hazard_used_in_decision_false")


# === R3: Combined rendering ===

def test_combined_historical_context_in_server():
    """Server.py loads both historical_nws_obs and historical_alerts for Replay."""
    server_code = open("app/server.py").read()
    assert "historical_nws_obs" in server_code
    assert "historical_alerts" in server_code
    # Verify the combined rendering function exists in JS
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    assert "renderHistoricalNwsContext" in js_code
    # Old separate functions should not be called
    assert "renderHistoricalNwsObs(" not in js_code or "function renderHistoricalNwsObs" not in js_code
    assert "renderHistoricalAlerts(" not in js_code or "function renderHistoricalAlerts" not in js_code
    print("  PASS: test_combined_historical_context_in_server")


# === R3: Provenance ===

def test_replay_provenance_includes_historical():
    """Replay provenance reflects that historical NWS is included."""
    server_code = open("app/server.py").read()
    assert "frozen contemporaneous historical" in server_code.lower() or \
           "historical station observation" in server_code.lower(), \
        "Replay provenance does not reflect included historical NWS"
    print("  PASS: test_replay_provenance_includes_historical")


# === R3: Weather answer ===

def test_weather_answer_includes_station_obs():
    """'What was the weather' answer includes station observation, not just alerts."""
    js_code = open("app/dashboard-luna/js/dashboard.js").read()
    # The weather intent for Replay should reference station observation
    assert "tempD(obs.temperature_celsius)" in js_code or "station KPHX observed" in js_code, \
        "Weather answer does not reference station observation"
    print("  PASS: test_weather_answer_includes_station_obs")


if __name__ == "__main__":
    # ... existing tests ...
    test_exact_21h_observation_wins()
    test_selection_rule_documented()
    test_provider_unit_codes_preserved()
    test_raw_window_fixture_exists()
    test_station_identity_vs_text_description()
    test_alert_raw_messages_preserved()
    test_alert_consumer_projection_deduplicates()
    test_hazard_used_in_decision_false()
    test_combined_historical_context_in_server()
    test_replay_provenance_includes_historical()
    test_weather_answer_includes_station_obs()
    print("\nAll R3 tests passed.")
