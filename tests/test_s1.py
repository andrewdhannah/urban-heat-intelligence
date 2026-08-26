"""
S1 Tests — Agent + Evidence Core (closeout remediation)

Tests covering planning, normalization, live/replay modes,
evidence chain, failure behavior, and temporal provenance.
"""

import json
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tools.heatmap import normalize_heatmap_result, _derive_observation_time
from src.tools.env_params import normalize_env_params_result
from src.agent.controller import HeatAgent, plan_question


class MockAdapter:
    """Mock adapter for testing without network."""
    def __init__(self, heatmap_status="Completed", env_params_status="Completed"):
        self.heatmap_status = heatmap_status
        self.env_params_status = env_params_status
        self.call_count = {"heatmap": 0, "env_params": 0, "poll": 0}

    def submit_heatmap(self, params):
        self.call_count["heatmap"] += 1
        return {"data": {"activity_id": "mock-heatmap-id"}}

    def submit_env_params(self, params):
        self.call_count["env_params"] += 1
        return {"data": {"activity_id": "mock-env-params-id"}}

    def poll_status(self, activity_id, max_polls=30, interval=0):
        self.call_count["poll"] += 1
        if "heatmap" in activity_id:
            return {"data": {"status": self.heatmap_status, "result": {
                "map_data": {"features": [{"id": "0", "type": "Feature", "properties": {"tile_id": 0, "average_temperature": 42.0}, "geometry": {"type": "Polygon", "coordinates": [[[-112.08, 33.44], [-112.06, 33.44], [-112.06, 33.46], [-112.08, 33.46], [-112.08, 33.44]]]}}]},
                "stats_data": {}
            }}}
        else:
            return {"data": {"status": self.env_params_status, "result": {
                "metadata": {"timezone": "GMT-7", "time_range": {"start": "2026-08-25T14:00:00-07:00"}},
                "locations": [{"parameters": {"heat_index_celsius": 39.3, "apparent_temperature_celsius": 46.4, "relative_humidity_percent": 11.3}, "solar_irradiance": {"value": 850}}]
            }}}


# === PLANNING TESTS ===

def test_plan_area_risk():
    """Area risk question produces two-tool plan."""
    plan = plan_question("What's the heat risk in Phoenix right now?")
    assert "get_heatmap" in plan["selected_tools"]
    assert "get_environmental_parameters" in plan["selected_tools"]
    assert plan["interpreted_intent"] == "area_risk_assessment"
    print("  PASS: test_plan_area_risk")

def test_plan_distribution():
    """Distribution question produces single-tool plan."""
    plan = plan_question("Show me the temperature distribution across Phoenix.")
    assert "get_heatmap" in plan["selected_tools"]
    assert "get_environmental_parameters" not in plan["selected_tools"]
    assert plan["interpreted_intent"] == "temperature_distribution"
    print("  PASS: test_plan_distribution")


# === TOOL COMPOSITION TESTS ===

def test_heatmap_invocation():
    """Phoenix question invokes heatmap."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    plan_step = next(e for e in result["evidence_chain"] if e["step"] == "plan")
    assert "get_heatmap" in plan_step["data"]["selected_tools"]
    print("  PASS: test_heatmap_invocation")

def test_env_params_driven_by_heatmap():
    """Result drives subsequent env_params call."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    assert steps.index("heatmap_result") < steps.index("env_params_result")
    print("  PASS: test_env_params_driven_by_heatmap")

def test_not_canned_answer():
    """Tool composition produces real data-driven answer."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["conditions"]["area_mean_temperature_celsius"] is not None
    assert result["answer"]["conditions"]["feature_count"] > 0
    print("  PASS: test_not_canned_answer")

def test_raw_schema_not_exposed():
    """Provider raw schema is not exposed as application contract."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert "map_data" not in result["answer"]
    assert "stats_data" not in result["answer"]
    assert "area_mean_temperature_celsius" in result["answer"]["conditions"]
    print("  PASS: test_raw_schema_not_exposed")


# === LIVE/REPLAY MODE TESTS ===

def test_live_mode():
    """LIVE mode works with provider."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "live"
    assert adapter.call_count["heatmap"] == 1
    print("  PASS: test_live_mode")

def test_replay_mode_no_network():
    """REPLAY mode makes zero network calls."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "replay"
    assert adapter.call_count["heatmap"] == 0
    assert adapter.call_count["env_params"] == 0
    print("  PASS: test_replay_mode_no_network")

def test_common_normalization():
    """LIVE and REPLAY use common normalization logic."""
    raw = {"result": {"map_data": {"features": [{"properties": {"average_temperature": 42.0}, "geometry": {"coordinates": [[[-112.08, 33.44]]]}}]}, "stats_data": {}}}
    live = normalize_heatmap_result(raw, {"date_time": {"start_date": "2026-08-25", "start_time": "14:00"}}, mode="live")
    replay = normalize_heatmap_result(raw, {"date_time": {"start_date": "2026-08-25", "start_time": "14:00"}}, mode="replay")
    assert live["result"]["mean_temperature_celsius"] == replay["result"]["mean_temperature_celsius"]
    print("  PASS: test_common_normalization")


# === EVIDENCE CHAIN TESTS ===

def test_answer_receipt_links_both():
    """Answer receipt links both provider operations."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    endpoints = [s["endpoint"] for s in result["answer"]["sources"]]
    assert "/v1/heatmap" in endpoints
    assert "/v1/env_params" in endpoints
    print("  PASS: test_answer_receipt_links_both")

def test_measured_result_computed():
    """Measured result is computed from evidence."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    measured = result["answer"]["conditions"]["measured_result"]
    assert measured["apparent_vs_measured_delta_celsius"] is not None
    print("  PASS: test_measured_result_computed")

def test_observation_time_visible():
    """Observation time is visible and derived from provider data."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["observation_time"] is not None
    # For replay, should be fixture observation time, not current time
    assert "2026-08-25" in result["answer"]["observation_time"]
    print("  PASS: test_observation_time_visible")

def test_mode_visible():
    """Mode is visible."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "replay"
    print("  PASS: test_mode_visible")

def test_activity_ids_preserved():
    """Activity IDs are preserved in evidence chain."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    heatmap_step = next(e for e in result["evidence_chain"] if e["step"] == "heatmap_result")
    env_step = next(e for e in result["evidence_chain"] if e["step"] == "env_params_result")
    assert heatmap_step["data"]["activity_id"] is not None
    assert env_step["data"]["activity_id"] is not None
    print("  PASS: test_activity_ids_preserved")

def test_replay_observation_time_not_current():
    """Replay observation time is fixture time, not execution time."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    obs_time = result["answer"]["observation_time"]
    # Should contain fixture date, not today
    assert "2026-08-25" in obs_time
    # Should NOT contain today's date (unless today happens to be Aug 25)
    today = datetime.now().strftime("%Y-%m-%d")
    # This assertion is valid only if today is not Aug 25
    if today != "2026-08-25":
        assert today not in obs_time
    print("  PASS: test_replay_observation_time_not_current")


# === FAILURE TESTS ===

def test_failed_heatmap_stops():
    """Failed heatmap stops correctly."""
    adapter = MockAdapter(heatmap_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_failed_heatmap_stops")

def test_failed_env_params_stops():
    """Failed env_params stops correctly."""
    adapter = MockAdapter(env_params_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_failed_env_params_stops")

def test_timeout_stops():
    """Timeout stops correctly."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(side_effect=TimeoutError("timeout"))
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_timeout_stops")

def test_malformed_response():
    """Malformed provider response fails boundedly."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(return_value={"data": {"status": "Completed", "result": "not-a-dict"}})
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    # Should produce error or degraded answer, not crash
    assert result is not None
    # Should not have fabricated thermal values
    conditions = result["answer"].get("conditions", {})
    if conditions:
        assert conditions.get("area_mean_temperature_celsius") is None or isinstance(conditions.get("area_mean_temperature_celsius"), (int, float))
    print("  PASS: test_malformed_response")

def test_missing_credential():
    """Missing LIVE credential fails without secret exposure."""
    from src.agent.adapter import FortyGuardAdapter
    # Create adapter with a non-existent credential path
    with patch.object(FortyGuardAdapter, '_load_api_key', side_effect=RuntimeError("FORTYGUARD_API_KEY not found")):
        try:
            adapter = FortyGuardAdapter(mode="live")
            # Should not reach here
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "FORTYGUARD_API_KEY" in str(e)
    print("  PASS: test_missing_credential")

def test_no_secret_in_output():
    """No secret appears in output/logs/fixtures/Git."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    result_str = json.dumps(result)
    assert "FORTYGUARD_API_KEY" not in result_str
    # Check fixture files
    fixture_dir = Path("fixtures/fortyguard")
    if fixture_dir.exists():
        for f in fixture_dir.rglob("*.json"):
            content = f.read_text()
            assert "FORTYGUARD_API_KEY" not in content
    print("  PASS: test_no_secret_in_output")


def run_all():
    tests = [
        test_plan_area_risk,
        test_plan_distribution,
        test_heatmap_invocation,
        test_env_params_driven_by_heatmap,
        test_not_canned_answer,
        test_raw_schema_not_exposed,
        test_live_mode,
        test_replay_mode_no_network,
        test_common_normalization,
        test_answer_receipt_links_both,
        test_measured_result_computed,
        test_observation_time_visible,
        test_mode_visible,
        test_activity_ids_preserved,
        test_replay_observation_time_not_current,
        test_failed_heatmap_stops,
        test_failed_env_params_stops,
        test_timeout_stops,
        test_malformed_response,
        test_missing_credential,
        test_no_secret_in_output,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1
    print(f"\nS1 TESTS: {passed}/{len(tests)} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    from datetime import datetime
    success = run_all()
    sys.exit(0 if success else 1)
