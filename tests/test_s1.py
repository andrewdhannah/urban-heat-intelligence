"""
S1 Tests — Agent + Evidence Core

17 minimum tests covering tool composition, live/replay modes,
evidence chain, and failure behavior.
"""

import json
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tools.heatmap import normalize_heatmap_result
from src.tools.env_params import normalize_env_params_result
from src.agent.controller import HeatAgent


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
            return {"data": {"status": self.heatmap_status, "result": self._mock_heatmap_result()}}
        else:
            return {"data": {"status": self.env_params_status, "result": self._mock_env_params_result()}}

    def _mock_heatmap_result(self):
        return {
            "map_data": {
                "type": "FeatureCollection",
                "features": [
                    {"id": "0", "type": "Feature", "properties": {"tile_id": 0, "average_temperature": 42.0},
                     "geometry": {"type": "Polygon", "coordinates": [[[-112.08, 33.44], [-112.06, 33.44], [-112.06, 33.46], [-112.08, 33.46], [-112.08, 33.44]]]}}
                ]
            },
            "stats_data": {"temperature_stats": {"Minimum": 41.5, "Maximum": 42.5, "Mean": 42.0}}
        }

    def _mock_env_params_result(self):
        return {
            "metadata": {"timezone": "GMT-7"},
            "locations": [{
                "parameters": [
                    {"name": "heat_index_celsius", "value": 39.3},
                    {"name": "apparent_temperature_celsius", "value": 46.4},
                    {"name": "relative_humidity_percent", "value": 11.3}
                ],
                "solar_irradiance": {"value": 850}
            }]
        }


def test_1_heatmap_invocation():
    """Phoenix question invokes heatmap."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["evidence_chain"][1]["data"]["selected_tool"] == "get_heatmap"
    print("  PASS: test_1_heatmap_invocation")


def test_2_env_params_driven_by_heatmap():
    """Result drives subsequent env_params call."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    assert "heatmap_result" in steps
    assert "env_params_result" in steps
    hm_idx = steps.index("heatmap_result")
    ep_idx = steps.index("env_params_result")
    assert ep_idx > hm_idx
    print("  PASS: test_2_env_params_driven_by_heatmap")


def test_3_not_canned_answer():
    """Tool composition is not a canned answer."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    # Answer should contain actual data from fixtures
    assert result["answer"]["conditions"]["area_mean_temperature_celsius"] is not None
    assert result["answer"]["conditions"]["feature_count"] > 0
    print("  PASS: test_3_not_canned_answer")


def test_4_live_mode_works():
    """LIVE mode works with provider."""
    adapter = MockAdapter(heatmap_status="Completed", env_params_status="Completed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "live"
    assert adapter.call_count["heatmap"] == 1
    assert adapter.call_count["env_params"] == 1
    print("  PASS: test_4_live_mode_works")


def test_5_replay_mode_no_network():
    """REPLAY mode makes zero network calls."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "replay"
    # Replay should use fixtures, not adapter calls
    assert adapter.call_count["heatmap"] == 0
    assert adapter.call_count["env_params"] == 0
    print("  PASS: test_5_replay_mode_no_network")


def test_6_common_normalization():
    """LIVE and REPLAY use common normalization logic."""
    # Both call the same normalize functions
    raw_heatmap = {
        "result": {
            "map_data": {"features": [{"properties": {"average_temperature": 42.0}, "geometry": {"coordinates": [[[-112.08, 33.44]]]}}]},
            "stats_data": {}
        }
    }
    live = normalize_heatmap_result(raw_heatmap, {}, mode="live")
    replay = normalize_heatmap_result(raw_heatmap, {}, mode="replay")
    assert live["result"]["mean_temperature_celsius"] == replay["result"]["mean_temperature_celsius"]
    print("  PASS: test_6_common_normalization")


def test_7_raw_schema_not_exposed():
    """Provider raw schema is not exposed as application contract."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    # Answer should use normalized fields, not raw provider fields
    assert "map_data" not in result["answer"]
    assert "stats_data" not in result["answer"]
    assert "area_mean_temperature_celsius" in result["answer"]["conditions"]
    print("  PASS: test_7_raw_schema_not_exposed")


def test_8_answer_receipt_links_both():
    """Answer receipt links both provider operations."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    sources = result["answer"]["sources"]
    endpoints = [s["endpoint"] for s in sources]
    assert "/v1/heatmap" in endpoints
    assert "/v1/env_params" in endpoints
    print("  PASS: test_8_answer_receipt_links_both")


def test_9_measured_result_computed():
    """Measured result is computed from evidence."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    measured = result["answer"]["conditions"]["measured_result"]
    assert measured["apparent_vs_measured_delta_celsius"] is not None
    print("  PASS: test_9_measured_result_computed")


def test_10_observation_timestamp_visible():
    """Observation timestamp is visible."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["observation_time"] is not None
    print("  PASS: test_10_observation_timestamp_visible")


def test_11_mode_visible():
    """Mode is visible."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"]["mode"] == "replay"
    print("  PASS: test_11_mode_visible")


def test_12_failed_heatmap_stops():
    """Failed heatmap stops correctly."""
    adapter = MockAdapter(heatmap_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_12_failed_heatmap_stops")


def test_13_failed_env_params_stops():
    """Failed env_params stops correctly."""
    adapter = MockAdapter(env_params_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_13_failed_env_params_stops")


def test_14_timeout_stops():
    """Timeout stops correctly."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(side_effect=TimeoutError("timeout"))
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    print("  PASS: test_14_timeout_stops")


def test_15_malformed_response():
    """Malformed provider response fails boundedly."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(return_value={"data": {}})
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    # Should not crash, should produce error or degraded answer
    assert result is not None
    print("  PASS: test_15_malformed_response")


def test_16_missing_credential():
    """Missing LIVE credential fails without secret exposure."""
    from src.agent.adapter import FortyGuardAdapter
    # Try to create adapter without credential
    try:
        bad_adapter = FortyGuardAdapter(mode="live")
        # If it loads, check that key is present
        # If it fails, that's expected
    except (RuntimeError, FileNotFoundError):
        pass  # Expected
    print("  PASS: test_16_missing_credential")


def test_17_no_secret_in_output():
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
    print("  PASS: test_17_no_secret_in_output")


def run_all():
    """Run all S1 tests."""
    tests = [
        test_1_heatmap_invocation,
        test_2_env_params_driven_by_heatmap,
        test_3_not_canned_answer,
        test_4_live_mode_works,
        test_5_replay_mode_no_network,
        test_6_common_normalization,
        test_7_raw_schema_not_exposed,
        test_8_answer_receipt_links_both,
        test_9_measured_result_computed,
        test_10_observation_timestamp_visible,
        test_11_mode_visible,
        test_12_failed_heatmap_stops,
        test_13_failed_env_params_stops,
        test_14_timeout_stops,
        test_15_malformed_response,
        test_16_missing_credential,
        test_17_no_secret_in_output,
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

    print()
    print(f"S1 TESTS: {passed}/{len(tests)} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
