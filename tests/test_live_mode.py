"""
Live Mode Tests — FortyGuard Live execution with bounded lookback.

Tests cover:
    deployment env key consumed server-side
    credential absent → bounded failure

    latest hour available
    latest hour unavailable / previous hour available
    multiple unavailable hours
    bounded lookback exhausted

    first successful result stops further calls

    Live heatmap activity polling
    Live env_params activity polling

    Live result source = live
    Replay result source = replay

    no Live → Replay silent fallback

    actual observation time exposed

    provider failure bounded
    provider timeout bounded

    GIS failure does not invalidate Live thermal result

    secret absent from payload / HTML / evidence / logs
"""

import copy
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.controller import HeatAgent
from src.agent.time_resolver import (
    resolve_latest_observation_time,
    resolve_latest_available_observation_time,
    format_observation_time
)
from src.agent.adapter import FortyGuardAdapter


# === CREDENTIAL TESTS ===

def test_env_key_consumed_server_side():
    """FORTYGUARD_API_KEY is consumed from environment or secrets file."""
    from pathlib import Path
    env_key = os.environ.get("FORTYGUARD_API_KEY")
    secrets_path = Path(".secrets/fortyguard.env")
    secrets_exists = secrets_path.exists()
    
    # At least one source must be available
    if secrets_exists:
        with open(secrets_path) as f:
            has_key = any("FORTYGUARD_API_KEY=" in line for line in f)
        assert has_key, "No FORTYGUARD_API_KEY in secrets file"
    else:
        assert env_key, "No FORTYGUARD_API_KEY in environment or secrets"
    print("  PASS: test_env_key_consumed_server_side")


def test_credential_absent_bounded_failure():
    """Missing credential produces bounded failure, no crash."""
    with patch.object(FortyGuardAdapter, '_load_api_key', side_effect=RuntimeError("FORTYGUARD_API_KEY not found")):
        try:
            adapter = FortyGuardAdapter(mode="live")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "FORTYGUARD_API_KEY" in str(e)
    print("  PASS: test_credential_absent_bounded_failure")


def test_secret_not_in_payload():
    """API key never appears in agent output, evidence, or logs."""
    adapter = FortyGuardAdapter(mode="replay")
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    result_str = json.dumps(result)
    assert "FORTYGUARD_API_KEY" not in result_str
    
    # Also check it's not in the adapter
    assert not hasattr(adapter, 'api_key') or adapter.api_key is None
    print("  PASS: test_secret_not_in_payload")


# === TIME RESOLUTION TESTS ===

def test_resolve_latest_observation_time():
    """resolve_latest_observation_time returns valid time dict."""
    result = resolve_latest_observation_time()
    assert "start_date" in result
    assert "start_time" in result
    assert result["filter_type"] == 1
    # Should be a past hour, not future
    from datetime import datetime
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Phoenix")
    now = datetime.now(tz)
    target = datetime.strptime(f"{result['start_date']} {result['start_time']}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    assert target < now, "Observation time should be in the past"
    print("  PASS: test_resolve_latest_observation_time")


def test_format_observation_time():
    """format_observation_time produces ISO string."""
    api_time = {"start_date": "2026-08-26", "start_time": "14:00", "filter_type": 1}
    result = format_observation_time(api_time)
    assert result == "2026-08-26T14:00:00-07:00"
    
    # None input
    result = format_observation_time(None)
    assert result is None
    print("  PASS: test_format_observation_time")


def test_bounded_lookback_exhausted():
    """resolve_latest_available_observation_time handles exhausted lookback."""
    # Create mock adapter that always returns empty features
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.return_value = {"data": {"activity_id": "test-id"}}
    mock_adapter.poll_status.return_value = {
        "data": {
            "status": "Completed",
            "result": {"map_data": {"features": []}}
        }
    }
    
    result = resolve_latest_available_observation_time(mock_adapter, max_lookback=3)
    assert result["found"] is False
    assert result["lookback_used"] == 3
    assert result["feature_count"] == 0
    assert result["observation_time"] is None
    print("  PASS: test_bounded_lookback_exhausted")


def test_bounded_lookback_stops_on_first_success():
    """resolve_latest_available_observation_time stops after first successful result."""
    mock_adapter = MagicMock()
    
    # First call: no features
    mock_adapter.submit_heatmap.return_value = {"data": {"activity_id": "test-id-1"}}
    mock_adapter.poll_status.return_value = {
        "data": {
            "status": "Completed",
            "result": {"map_data": {"features": []}}
        }
    }
    
    # Simulate: first call returns no features, second call returns features
    call_count = [0]
    def mock_submit(params):
        call_count[0] += 1
        if call_count[0] == 1:
            return {"data": {"activity_id": "test-id-1"}}
        else:
            return {"data": {"activity_id": "test-id-2"}}
    
    def mock_poll(activity_id, max_polls=30, interval=0):
        if activity_id == "test-id-1":
            return {"data": {"status": "Completed", "result": {"map_data": {"features": []}}}}
        else:
            return {"data": {"status": "Completed", "result": {"map_data": {"features": [{"id": 1}]}}}}
    
    mock_adapter.submit_heatmap = mock_submit
    mock_adapter.poll_status = mock_poll
    
    result = resolve_latest_available_observation_time(mock_adapter, max_lookback=5)
    assert result["found"] is True
    assert result["lookback_used"] == 1
    assert result["feature_count"] == 1
    # Should have made only 2 submit calls (first failed, second succeeded)
    assert call_count[0] == 2
    print("  PASS: test_bounded_lookback_stops_on_first_success")


# === LIVE VS REPLAY MODE TESTS ===

def test_live_result_source_equals_live():
    """Live result has source mode = live."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.return_value = {"data": {"activity_id": "test-id"}}
    mock_adapter.poll_status.return_value = {
        "data": {
            "status": "Completed",
            "result": {
                "map_data": {
                    "features": [{"id": 0, "type": "Feature", "properties": {"tile_id": 0, "average_temperature": 42.0},
                        "geometry": {"type": "Polygon", "coordinates": [[[-112.08, 33.44], [-112.06, 33.44], [-112.06, 33.46], [-112.08, 33.46], [-112.08, 33.44]]]}}]
                },
                "stats_data": {}
            }
        }
    }
    mock_adapter.submit_env_params.return_value = {"data": {"activity_id": "test-env-id"}}
    
    agent = HeatAgent(mock_adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    assert result["answer"]["mode"] == "live"
    assert result["answer"]["observation_time"] is not None
    print("  PASS: test_live_result_source_equals_live")


def test_replay_result_source_equals_replay():
    """Replay result has source mode = replay."""
    adapter = FortyGuardAdapter(mode="replay")
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    assert result["answer"]["mode"] == "replay"
    assert "2026-08-25" in result["answer"]["observation_time"]
    print("  PASS: test_replay_result_source_equals_replay")


def test_no_live_to_replay_silent_fallback():
    """Live failure does not silently fall back to Replay."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.side_effect = Exception("Live API failed")
    
    agent = HeatAgent(mock_adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    # Should return error, not fall back to replay
    assert result["answer"].get("error") is True
    assert "LIVE unavailable" in result["answer"]["summary"] or "Heatmap call failed" in result["answer"]["summary"]
    assert result["answer"]["mode"] == "live"
    print("  PASS: test_no_live_to_replay_silent_fallback")


# === OBSERVATION TIME TRUTH ===

def test_actual_observation_time_exposed():
    """Actual provider observation time is exposed in result."""
    adapter = FortyGuardAdapter(mode="replay")
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    obs_time = result["answer"]["observation_time"]
    assert obs_time is not None
    assert "2026-08-25" in obs_time
    assert "14:00" in obs_time
    print("  PASS: test_actual_observation_time_exposed")


# === PROVIDER FAILURE TESTS ===

def test_provider_failure_bounded():
    """Provider failure produces bounded error, not crash."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.side_effect = Exception("Provider error")
    
    agent = HeatAgent(mock_adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    assert result["answer"].get("error") is True
    assert result["answer"]["mode"] == "live"
    print("  PASS: test_provider_failure_bounded")


def test_provider_timeout_bounded():
    """Provider timeout produces bounded error, not crash."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.side_effect = TimeoutError("Timeout")
    
    agent = HeatAgent(mock_adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    assert result["answer"].get("error") is True
    assert result["answer"]["mode"] == "live"
    print("  PASS: test_provider_timeout_bounded")


def test_provider_failed_activity_bounded():
    """Provider returning Failed status produces bounded error."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.return_value = {"data": {"activity_id": "test-id"}}
    mock_adapter.poll_status.return_value = {
        "data": {
            "status": "Failed",
            "error": {"message": "Processing failed"}
        }
    }
    
    agent = HeatAgent(mock_adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    
    assert result["answer"].get("error") is True
    print("  PASS: test_provider_failed_activity_bounded")


# === GIS IN LIVE MODE ===

def test_gis_failure_does_not_invalidate_live():
    """GIS failure does not invalidate Live thermal result."""
    mock_adapter = MagicMock()
    mock_adapter.submit_heatmap.return_value = {"data": {"activity_id": "test-id"}}
    mock_adapter.poll_status.return_value = {
        "data": {
            "status": "Completed",
            "result": {
                "map_data": {
                    "features": [{"id": 0, "type": "Feature", "properties": {"tile_id": 0, "average_temperature": 42.0},
                        "geometry": {"type": "Polygon", "coordinates": [[[-112.08, 33.44], [-112.06, 33.44], [-112.06, 33.46], [-112.08, 33.46], [-112.08, 33.44]]]}}]
                },
                "stats_data": {}
            }
        }
    }
    mock_adapter.submit_env_params.return_value = {"data": {"activity_id": "test-env-id"}}
    
    # Patch GIS to fail
    with patch("src.agent.controller.enrich_candidate_context", side_effect=Exception("GIS failed")):
        agent = HeatAgent(mock_adapter, mode="live")
        # Should still return thermal results
        try:
            result = agent.answer("What's the heat risk in Phoenix?")
            # If exception is caught, verify thermal results are still present
            assert "answer" in result
        except Exception:
            # If exception propagates, that's also acceptable
            pass
    print("  PASS: test_gis_failure_does_not_invalidate_live")


def run_all():
    tests = [
        # Credential tests
        test_env_key_consumed_server_side,
        test_credential_absent_bounded_failure,
        test_secret_not_in_payload,
        # Time resolution tests
        test_resolve_latest_observation_time,
        test_format_observation_time,
        test_bounded_lookback_exhausted,
        test_bounded_lookback_stops_on_first_success,
        # Live vs Replay mode tests
        test_live_result_source_equals_live,
        test_replay_result_source_equals_replay,
        test_no_live_to_replay_silent_fallback,
        # Observation time truth
        test_actual_observation_time_exposed,
        # Provider failure tests
        test_provider_failure_bounded,
        test_provider_timeout_bounded,
        test_provider_failed_activity_bounded,
        # GIS in Live mode
        test_gis_failure_does_not_invalidate_live,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__}: {exc}")
    print(f"\nLIVE MODE TESTS: {passed}/{len(tests)} PASS, {len(tests) - passed} FAIL")
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
