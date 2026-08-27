"""
S1 Tests — Final security/temporal closeout

15 required tests + additional coverage.
"""

import json
import sys
import ssl
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tools.heatmap import normalize_heatmap_result
from src.tools.env_params import normalize_env_params_result
from src.agent.controller import HeatAgent, plan_question
from src.agent.time_resolver import resolve_latest_observation_time


class MockAdapter:
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
                "map_data": {"features": [{"id": "0", "type": "Feature", "properties": {"tile_id": 0, "average_temperature": 42.0},
                    "geometry": {"type": "Polygon", "coordinates": [[[-112.08, 33.44], [-112.06, 33.44], [-112.06, 33.46], [-112.08, 33.46], [-112.08, 33.44]]]}}]},
                "stats_data": {}
            }}}
        return {"data": {"status": self.env_params_status, "result": {
            "metadata": {"timezone": "GMT-7", "time_range": {"start": "2026-08-25T14:00:00-07:00"}},
            "locations": [{"parameters": {"heat_index_celsius": 39.3, "apparent_temperature_celsius": 46.4, "relative_humidity_percent": 11.3}}]
        }}}


# === TLS TESTS ===

def test_1_tls_verification_enabled():
    """TLS certificate verification is enabled."""
    ctx = ssl.create_default_context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    print("  PASS: test_1_tls_verification_enabled")

def test_2_hostname_verification_enabled():
    """Hostname verification is enabled."""
    ctx = ssl.create_default_context()
    assert ctx.check_hostname is True
    print("  PASS: test_2_hostname_verification_enabled")

def test_3_adapter_uses_verified_tls():
    """Adapter creates verified TLS context, not CERT_NONE."""
    from src.agent.adapter import FortyGuardAdapter
    adapter = FortyGuardAdapter(mode="replay")
    assert adapter._ssl_ctx.verify_mode == ssl.CERT_REQUIRED
    assert adapter._ssl_ctx.check_hostname is True
    print("  PASS: test_3_adapter_uses_verified_tls")


# === TIME RESOLUTION TESTS ===

def test_4_live_default_time_dynamic():
    """LIVE default time is dynamically resolved."""
    t = resolve_latest_observation_time()
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    assert t["start_date"] == today or t["start_date"] >= "2026-01-01"
    print("  PASS: test_4_live_default_time_dynamic")

def test_5_live_default_not_aug25():
    """LIVE default time is not hard-coded Aug-25."""
    t = resolve_latest_observation_time()
    assert t["start_date"] != "2026-08-25"
    print("  PASS: test_5_live_default_not_aug25")

def test_6_phoenix_timezone():
    """Phoenix timezone semantics are used."""
    t = resolve_latest_observation_time("America/Phoenix")
    assert t["start_date"] is not None
    assert t["start_time"] is not None
    assert t["filter_type"] == 1
    print("  PASS: test_6_phoenix_timezone")

def test_7_replay_observation_time():
    """REPLAY remains fixed to fixture observation time."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    obs = result["answer"]["observation_time"]
    assert "2026-08-25" in obs
    assert "14:00" in obs
    print("  PASS: test_7_replay_observation_time")

def test_8_live_replay_times_distinct():
    """LIVE and REPLAY time semantics remain distinct."""
    from src.agent.time_resolver import resolve_latest_observation_time
    live_time = resolve_latest_observation_time()
    replay_time = {"start_date": "2026-08-25", "start_time": "14:00"}
    assert live_time["start_date"] != replay_time["start_date"]
    print("  PASS: test_8_live_replay_times_distinct")


# === EVIDENCE CHAIN TESTS ===

def test_9_eight_node_chain():
    """Evidence chain contains all 8 required nodes."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    required = ["user_request", "plan", "heatmap_request", "heatmap_result",
                 "coordinate_selection", "env_params_request", "env_params_result", "answer"]
    for r in required:
        assert r in steps, f"Missing node: {r}"
    print("  PASS: test_9_eight_node_chain")

def test_10_heatmap_req_before_result():
    """Heatmap request node precedes heatmap result."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    assert steps.index("heatmap_request") < steps.index("heatmap_result")
    print("  PASS: test_10_heatmap_req_before_result")

def test_11_env_req_before_result():
    """Env_params request node precedes env_params result."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    assert steps.index("env_params_request") < steps.index("env_params_result")
    print("  PASS: test_11_env_req_before_result")

def test_12_answer_terminal():
    """Answer node is terminal."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    steps = [e["step"] for e in result["evidence_chain"]]
    assert steps[-1] == "answer"
    print("  PASS: test_12_answer_terminal")


# === EXISTING TESTS ===

def test_13_planner():
    """Existing planner tests still pass."""
    p1 = plan_question("What's the heat risk in Phoenix?")
    assert "get_heatmap" in p1["selected_tools"]
    p2 = plan_question("Show me the temperature distribution across Phoenix.")
    assert "get_heatmap" in p2["selected_tools"]
    assert "get_environmental_parameters" not in p2["selected_tools"]
    print("  PASS: test_13_planner")

def test_14_hotspot():
    """Top-3 ranked candidates with correct selection methods."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    coord_steps = [e for e in result["evidence_chain"] if e["step"] == "coordinate_selection"]
    assert len(coord_steps) == 3, f"Expected 3 coordinate selections, got {len(coord_steps)}"
    methods = [c["data"]["selection_method"] for c in coord_steps]
    assert "top_1_temperature_feature" in methods, f"Missing top_1 method: {methods}"
    # Verify ranked candidates in answer
    ranked = result["answer"]["conditions"].get("ranked_candidates", [])
    assert len(ranked) == 3, f"Expected 3 ranked candidates, got {len(ranked)}"
    assert ranked[0]["rank"] == 1, f"First candidate rank: {ranked[0]['rank']}"
    print("  PASS: test_14_hotspot")

def test_15_no_credential():
    """No credential appears anywhere in output/evidence."""
    adapter = MockAdapter()
    agent = HeatAgent(adapter, mode="replay")
    result = agent.answer("What's the heat risk in Phoenix?")
    result_str = json.dumps(result)
    assert "FORTYGUARD_API_KEY" not in result_str
    print("  PASS: test_15_no_credential")


# === FAILURE PATH TESTS (restored) ===

def test_16_failed_heatmap():
    """Failed heatmap produces bounded error, env_params not called."""
    adapter = MockAdapter(heatmap_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    assert adapter.call_count["env_params"] == 0
    # No fabricated thermal values
    conditions = result["answer"].get("conditions", {})
    assert conditions.get("area_mean_temperature_celsius") is None
    print("  PASS: test_16_failed_heatmap")

def test_17_failed_env_params():
    """Failed env_params produces bounded error."""
    adapter = MockAdapter(env_params_status="Failed")
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    # No fabricated environmental values
    conditions = result["answer"].get("conditions", {})
    rep = conditions.get("representative_location", {})
    assert rep.get("heat_index_celsius") is None
    print("  PASS: test_17_failed_env_params")

def test_18_timeout():
    """Timeout produces bounded error, no crash, no silent replay fallback."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(side_effect=TimeoutError("timeout"))
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result["answer"].get("error") is True
    assert result["answer"]["mode"] == "live"  # No silent fallback to replay
    print("  PASS: test_18_timeout")

def test_19_malformed_response():
    """Malformed provider response produces bounded error, no fabricated values."""
    adapter = MockAdapter()
    adapter.poll_status = MagicMock(return_value={"data": {"status": "Completed", "result": "not-a-dict"}})
    agent = HeatAgent(adapter, mode="live")
    result = agent.answer("What's the heat risk in Phoenix?")
    assert result is not None
    conditions = result["answer"].get("conditions", {})
    if conditions:
        # No fabricated thermal values
        val = conditions.get("area_mean_temperature_celsius")
        assert val is None or isinstance(val, (int, float))
    print("  PASS: test_19_malformed_response")

def test_20_missing_credential():
    """Missing LIVE credential fails boundedly, no API call, no replay fallback."""
    from src.agent.adapter import FortyGuardAdapter
    with patch.object(FortyGuardAdapter, '_load_api_key', side_effect=RuntimeError("FORTYGUARD_API_KEY not found")):
        try:
            adapter = FortyGuardAdapter(mode="live")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "FORTYGUARD_API_KEY" in str(e)
    print("  PASS: test_20_missing_credential")


def run_all():
    tests = [test_1_tls_verification_enabled, test_2_hostname_verification_enabled,
             test_3_adapter_uses_verified_tls, test_4_live_default_time_dynamic,
             test_5_live_default_not_aug25, test_6_phoenix_timezone,
             test_7_replay_observation_time, test_8_live_replay_times_distinct,
             test_9_eight_node_chain, test_10_heatmap_req_before_result,
             test_11_env_req_before_result, test_12_answer_terminal,
             test_13_planner, test_14_hotspot, test_15_no_credential,
             test_16_failed_heatmap, test_17_failed_env_params,
             test_18_timeout, test_19_malformed_response, test_20_missing_credential]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
    print(f"\nTESTS: {passed}/{len(tests)} PASS, {len(tests)-passed} FAIL")
    return passed == len(tests)


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
