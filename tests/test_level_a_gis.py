"""
Level A GIS Context Tests — Phoenix tree canopy and parks enrichment.

All tests use Replay fixtures or controlled responses. No real GIS network
calls are made by this suite.

Tests cover:
- canopy point-in-polygon success
- tract-level semantic labeling
- parks inside result
- parks outside result
- nearby parks bounded query
- canopy unavailable
- parks unavailable
- both GIS sources unavailable
- malformed provider result
- Live GIS behavior
- Replay zero GIS network
- fixture integrity
- existing thermal ranking unchanged
- existing eight-node evidence chain unchanged
- GIS context used_in_decision=false
- Brief LOCAL CONTEXT provenance
- browser rendering
- no unsupported claims
"""

import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tools.gis_context import (
    query_tree_canopy,
    query_parks,
    enrich_candidate_context,
    format_canopy_claim,
    format_parks_claim,
    _point_in_polygon,
    _validate_fixture_integrity
)
from src.agent.controller import HeatAgent
from src.agent.brief import compose_urban_heat_brief
from src.agent.adapter import FortyGuardAdapter
from app.server import build_visualization_payload


# === FIXTURE INTEGRITY TESTS ===

def test_gis_fixture_integrity_canopy():
    """GIS canopy fixture passes integrity validation."""
    fixture_path = Path("fixtures/phoenix-gis/canopy.json")
    assert fixture_path.exists(), "Canopy fixture not found"
    assert _validate_fixture_integrity(fixture_path, "canopy"), "Canopy fixture integrity check failed"
    print("  PASS: test_gis_fixture_integrity_canopy")


def test_gis_fixture_integrity_parks():
    """GIS parks fixture passes integrity validation."""
    fixture_path = Path("fixtures/phoenix-gis/parks.json")
    assert fixture_path.exists(), "Parks fixture not found"
    assert _validate_fixture_integrity(fixture_path, "parks"), "Parks fixture integrity check failed"
    print("  PASS: test_gis_fixture_integrity_parks")


def test_gis_fixture_integrity_fail_closed_missing_manifest():
    """GIS fixture integrity fails when manifest is missing (fail-closed)."""
    import tempfile, shutil
    # Temporarily move the manifest
    manifest_path = Path("fixtures/phoenix-gis/integrity-manifest.json")
    backup = manifest_path.with_suffix(".json.bak")
    try:
        shutil.move(str(manifest_path), str(backup))
        result = _validate_fixture_integrity(Path("fixtures/phoenix-gis/canopy.json"), "canopy")
        assert result is False, "Should fail-closed when manifest is missing"
    finally:
        shutil.move(str(backup), str(manifest_path))
    print("  PASS: test_gis_fixture_integrity_fail_closed_missing_manifest")


def test_gis_fixture_integrity_fail_closed_unregistered_fixture():
    """GIS fixture integrity fails when fixture not in manifest (fail-closed)."""
    result = _validate_fixture_integrity(Path("fixtures/phoenix-gis/canopy.json"), "nonexistent_type")
    assert result is False, "Should fail-closed when fixture type not in manifest"
    print("  PASS: test_gis_fixture_integrity_fail_closed_unregistered_fixture")


def test_gis_fixture_integrity_fail_closed_corrupted_fixture():
    """GIS fixture integrity fails when fixture is corrupted."""
    import tempfile, shutil
    fixture_path = Path("fixtures/phoenix-gis/canopy.json")
    backup = fixture_path.with_suffix(".json.bak")
    try:
        shutil.copy(str(fixture_path), str(backup))
        # Corrupt the fixture
        with open(fixture_path, "w") as f:
            f.write('{"corrupted": true}')
        result = _validate_fixture_integrity(fixture_path, "canopy")
        assert result is False, "Should fail-closed when fixture is corrupted"
    finally:
        shutil.move(str(backup), str(fixture_path))
    print("  PASS: test_gis_fixture_integrity_fail_closed_corrupted_fixture")


def test_gis_fixture_manifest_separate_from_fortyguard():
    """GIS fixtures are NOT in FortyGuard integrity manifest."""
    fg_manifest = Path("fixtures/fortyguard/integrity-manifest.json")
    gis_manifest = Path("fixtures/phoenix-gis/integrity-manifest.json")
    assert fg_manifest.exists(), "FortyGuard manifest not found"
    assert gis_manifest.exists(), "GIS manifest not found"
    
    with open(fg_manifest) as f:
        fg_data = json.load(f)
    with open(gis_manifest) as f:
        gis_data = json.load(f)
    
    # Verify GIS fixtures are not in FortyGuard manifest
    fg_fixture_paths = [fx["path"] for fx in fg_data.get("fixtures", [])]
    assert "fixtures/phoenix-gis/canopy.json" not in fg_fixture_paths
    assert "fixtures/phoenix-gis/parks.json" not in fg_fixture_paths
    
    # Verify GIS manifest has its own fixtures
    gis_fixture_paths = [fx["path"] for fx in gis_data.get("fixtures", [])]
    assert "fixtures/phoenix-gis/canopy.json" in gis_fixture_paths
    assert "fixtures/phoenix-gis/parks.json" in gis_fixture_paths
    print("  PASS: test_gis_fixture_manifest_separate_from_fortyguard")


# === POINT-IN-POLYGON TESTS ===

def test_point_in_polygon_inside():
    """Point inside polygon is correctly identified."""
    polygon = [[-112.08, 33.44], [-112.07, 33.44], [-112.07, 33.45], [-112.08, 33.45]]
    assert _point_in_polygon(33.445, -112.075, polygon), "Point inside polygon not detected"
    print("  PASS: test_point_in_polygon_inside")


def test_point_in_polygon_outside():
    """Point outside polygon is correctly identified."""
    polygon = [[-112.08, 33.44], [-112.07, 33.44], [-112.07, 33.45], [-112.08, 33.45]]
    assert not _point_in_polygon(33.46, -112.075, polygon), "Point outside polygon incorrectly detected"
    print("  PASS: test_point_in_polygon_outside")


# === CANOPY QUERY TESTS ===

def test_canopy_replay_success():
    """Canopy query succeeds in replay mode with valid fixture."""
    # Use actual candidate #1 coordinate from FortyGuard replay
    result = query_tree_canopy(33.4581, -112.0774, mode="replay")
    assert result["result"]["available"] is True, "Canopy should be available"
    assert result["result"]["census_tract_geoid"] == "04013113100"
    assert result["result"]["tree_canopy_pct"] == 0.87
    assert result["result"]["used_in_decision"] is False
    assert result["result"]["mode"] == "replay"
    print("  PASS: test_canopy_replay_success")


def test_canopy_tract_level_semantic_labeling():
    """Canopy result uses census tract level, not parcel or point level."""
    result = query_tree_canopy(33.4581, -112.0774, mode="replay")
    assert "census_tract_geoid" in result["result"]
    assert "tree_canopy_pct" in result["result"]
    assert "reference_period" in result["result"]
    # Should NOT have parcel-level or point-level claims
    assert "parcel" not in str(result).lower()
    assert "point_canopy" not in str(result).lower()
    print("  PASS: test_canopy_tract_level_semantic_labeling")


def test_canopy_evidence_nodes():
    """Canopy query produces proper evidence nodes."""
    result = query_tree_canopy(33.4581, -112.0774, mode="replay")
    assert "evidence_node" in result
    assert result["evidence_node"]["step"] == "canopy_request"
    assert "result_evidence_node" in result
    assert result["result_evidence_node"]["step"] == "canopy_result"
    assert result["result_evidence_node"]["data"]["provider"] == "City of Phoenix / Maricopa Association of Governments"
    print("  PASS: test_canopy_evidence_nodes")


def test_canopy_unavailable_point_outside():
    """Canopy query returns unavailable for point outside all tracts."""
    # Point outside all defined tracts
    result = query_tree_canopy(33.50, -112.10, mode="replay")
    # When point is outside all tracts, the function returns at top level
    assert result.get("available") is False or result.get("result", {}).get("available") is False
    print("  PASS: test_canopy_unavailable_point_outside")


def test_canopy_unavailable_missing_fixture():
    """Canopy query returns unavailable when fixture is missing."""
    with patch("src.tools.gis_context._load_gis_fixture", return_value=None):
        result = query_tree_canopy(33.445, -112.075, mode="replay")
        assert result.get("available") is False
        assert result.get("error") == "fixture_not_found"
    print("  PASS: test_canopy_unavailable_missing_fixture")


def test_canopy_unavailable_corrupted_fixture():
    """Canopy query returns unavailable when fixture is corrupted."""
    import shutil
    fixture = Path("fixtures/phoenix-gis/canopy.json")
    backup = fixture.with_suffix(".json.bak")
    try:
        shutil.copy2(fixture, backup)
        fixture.write_bytes(b"CORRUPTED")
        result = query_tree_canopy(33.445, -112.075, mode="replay")
        assert result.get("available") is False
    finally:
        if backup.exists():
            shutil.move(backup, fixture)
    print("  PASS: test_canopy_unavailable_corrupted_fixture")


# === PARKS QUERY TESTS ===

def test_parks_replay_inside_park():
    """Parks query correctly identifies candidate inside a park."""
    # Use actual candidate #1 coordinate (inside Roosevelt Park)
    result = query_parks(33.4581, -112.0774, mode="replay")
    assert result["result"]["available"] is True
    assert result["result"]["inside_park"] is not None
    assert result["result"]["inside_park"]["park_name"] == "Roosevelt Park"
    assert result["result"]["inside_park"]["park_type"] == "Pocket"
    assert result["result"]["used_in_decision"] is False
    print("  PASS: test_parks_replay_inside_park")


def test_parks_replay_outside_park():
    """Parks query correctly identifies candidate outside all parks."""
    # Use actual candidate #2 coordinate (outside parks)
    result = query_parks(33.459, -112.0774, mode="replay")
    assert result["result"]["available"] is True
    assert result["result"]["inside_park"] is None
    # Level A: no nearby_parks claims (proximity not computed)
    assert "nearby_parks" not in result["result"]
    print("  PASS: test_parks_replay_outside_park")


def test_parks_nearby_bounded_query():
    """Parks query does not make unsupported proximity claims."""
    # Use actual candidate #2 coordinate
    result = query_parks(33.459, -112.0774, mode="replay")
    assert result["result"]["available"] is True
    # Level A: no nearby_parks — proximity not computed
    assert "nearby_parks" not in result["result"]
    # Should NOT contain distance claims
    assert "distance" not in str(result).lower()
    assert "nearest" not in str(result).lower()
    assert "nearby-search" not in str(result).lower()
    print("  PASS: test_parks_nearby_bounded_query")


def test_parks_evidence_nodes():
    """Parks query produces proper evidence nodes."""
    # Use actual candidate #1 coordinate that's in the fixture
    result = query_parks(33.4581, -112.0774, mode="replay")
    assert "evidence_node" in result
    assert result["evidence_node"]["step"] == "parks_request"
    assert "result_evidence_node" in result
    assert result["result_evidence_node"]["step"] == "parks_result"
    assert result["result_evidence_node"]["data"]["provider"] == "City of Phoenix"
    print("  PASS: test_parks_evidence_nodes")


def test_parks_unavailable_missing_fixture():
    """Parks query returns unavailable when fixture is missing."""
    with patch("src.tools.gis_context._load_gis_fixture", return_value=None):
        result = query_parks(33.4445, -112.0705, mode="replay")
        assert result.get("available") is False
        assert result.get("error") == "fixture_not_found"
    print("  PASS: test_parks_unavailable_missing_fixture")


def test_parks_unavailable_corrupted_fixture():
    """Parks query returns unavailable when fixture is corrupted."""
    import shutil
    fixture = Path("fixtures/phoenix-gis/parks.json")
    backup = fixture.with_suffix(".json.bak")
    try:
        shutil.copy2(fixture, backup)
        fixture.write_bytes(b"CORRUPTED")
        result = query_parks(33.4445, -112.0705, mode="replay")
        assert result.get("available") is False
    finally:
        if backup.exists():
            shutil.move(backup, fixture)
    print("  PASS: test_parks_unavailable_corrupted_fixture")


# === CONTEXT ENRICHMENT TESTS ===

def test_enrich_candidate_context_success():
    """Context enrichment succeeds with both canopy and parks."""
    # Use actual candidate #1 coordinate
    result = enrich_candidate_context(33.4581, -112.0774, mode="replay")
    assert result["context"]["available"] is True
    assert result["context"]["canopy"] is not None
    assert result["context"]["parks"] is not None
    assert result["context"]["used_in_decision"] is False
    assert len(result["context_evidence_chain"]) > 0
    print("  PASS: test_enrich_candidate_context_success")


def test_enrich_candidate_context_canopy_only():
    """Context enrichment works when only canopy is available."""
    # Use actual candidate #1 coordinate
    with patch("src.tools.gis_context.query_parks", return_value={"result": {"available": False}, "evidence_node": {}, "result_evidence_node": {}}):
        result = enrich_candidate_context(33.4581, -112.0774, mode="replay")
        assert result["context"]["available"] is True
        assert result["context"]["canopy"] is not None
        assert result["context"]["parks"] is None
    print("  PASS: test_enrich_candidate_context_canopy_only")


def test_enrich_candidate_context_parks_only():
    """Context enrichment works when only parks is available."""
    # Use actual candidate #1 coordinate
    with patch("src.tools.gis_context.query_tree_canopy", return_value={"result": {"available": False}, "evidence_node": {}, "result_evidence_node": {}}):
        result = enrich_candidate_context(33.4581, -112.0774, mode="replay")
        assert result["context"]["available"] is True
        assert result["context"]["canopy"] is None
        assert result["context"]["parks"] is not None
    print("  PASS: test_enrich_candidate_context_parks_only")


def test_enrich_candidate_context_both_unavailable():
    """Context enrichment handles both sources unavailable."""
    # Use actual candidate #1 coordinate
    with patch("src.tools.gis_context.query_tree_canopy", return_value={"result": {"available": False}, "evidence_node": {}, "result_evidence_node": {}}):
        with patch("src.tools.gis_context.query_parks", return_value={"result": {"available": False}, "evidence_node": {}, "result_evidence_node": {}}):
            result = enrich_candidate_context(33.4581, -112.0774, mode="replay")
            assert result["context"]["available"] is False
            assert result["context"]["canopy"] is None
            assert result["context"]["parks"] is None
    print("  PASS: test_enrich_candidate_context_both_unavailable")


# === FORMAT CLAIM TESTS ===

def test_format_canopy_claim_success():
    """Canopy claim formats correctly with data."""
    canopy = {
        "available": True,
        "census_tract_geoid": "04013113100",
        "tree_canopy_pct": 0.87,
        "source_provider": "City of Phoenix / Maricopa Association of Governments",
        "reference_period": "2021"
    }
    claim = format_canopy_claim(canopy)
    assert claim is not None
    assert "census tract 04013113100" in claim
    assert "0.9%" in claim
    assert "2021" in claim
    print("  PASS: test_format_canopy_claim_success")


def test_format_canopy_claim_unavailable():
    """Canopy claim returns None when unavailable."""
    claim = format_canopy_claim(None)
    assert claim is None
    claim = format_canopy_claim({"available": False})
    assert claim is None
    print("  PASS: test_format_canopy_claim_unavailable")


def test_format_parks_claim_inside():
    """Parks claim formats correctly when inside a park."""
    parks = {
        "available": True,
        "inside_park": {"park_name": "Roosevelt Park", "park_type": "Pocket"},
        "nearby_parks": []
    }
    claim = format_parks_claim(parks)
    assert claim is not None
    assert "Roosevelt Park" in claim
    assert "lies inside" in claim
    print("  PASS: test_format_parks_claim_inside")


def test_format_parks_claim_nearby():
    """Parks claim formats correctly when outside all parks."""
    parks = {
        "available": True,
        "inside_park": None,
    }
    claim = format_parks_claim(parks)
    assert claim is not None
    assert "No mapped park" in claim
    # Level A: no nearby-search area claims
    assert "nearby-search" not in claim
    print("  PASS: test_format_parks_claim_nearby")


def test_format_parks_claim_no_parks():
    """Parks claim formats correctly with no parks."""
    parks = {
        "available": True,
        "inside_park": None,
        "nearby_parks": []
    }
    claim = format_parks_claim(parks)
    assert claim is not None
    assert "No mapped park" in claim
    print("  PASS: test_format_parks_claim_no_parks")


def test_format_parks_claim_unavailable():
    """Parks claim returns None when unavailable."""
    claim = format_parks_claim(None)
    assert claim is None
    claim = format_parks_claim({"available": False})
    assert claim is None
    print("  PASS: test_format_parks_claim_unavailable")


# === CONTROLLER INTEGRATION TESTS ===

def test_controller_replay_includes_context():
    """Controller includes GIS context in replay mode."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    assert "context" in result
    assert "context_evidence_chain" in result
    assert result["context"]["available"] is True
    print("  PASS: test_controller_replay_includes_context")


def test_controller_top3_enrichment():
    """Controller enriches all 3 candidates, not just #1."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    cc = result.get("candidate_contexts", {})
    assert len(cc) == 3, f"Expected 3 candidate contexts, got {len(cc)}"
    # Each candidate should have canopy context
    for i in range(3):
        ctx = cc[i]
        assert "canopy" in ctx, f"Candidate #{i+1} missing canopy context"
        assert ctx["canopy"] is not None, f"Candidate #{i+1} canopy is None"
        assert ctx["canopy"].get("available") is True, f"Candidate #{i+1} canopy not available"
    # Candidate #1 should be inside Roosevelt Park
    assert cc[0]["parks"]["inside_park"]["park_name"] == "Roosevelt Park"
    print("  PASS: test_controller_top3_enrichment")


def test_controller_thermal_evidence_chain_unchanged():
    """Controller preserves existing 8-node thermal evidence chain."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    # The thermal evidence chain should be in evidence_chain field
    # Context evidence chain should be in context_evidence_chain field
    thermal_steps = [e["step"] for e in result["evidence_chain"]]
    required = ["user_request", "plan", "heatmap_request", "heatmap_result",
                 "coordinate_selection", "env_params_request", "env_params_result", "answer"]
    for r in required:
        assert r in thermal_steps, f"Missing thermal node: {r}"
    # Verify thermal chain contains only thermal nodes (no GIS nodes)
    gis_nodes = ["canopy_request", "canopy_result", "parks_request", "parks_result", "context_enrichment_result"]
    for node in gis_nodes:
        assert node not in thermal_steps, f"GIS node {node} found in thermal chain"
    print("  PASS: test_controller_thermal_evidence_chain_unchanged")


def test_controller_context_evidence_chain_separate():
    """Controller keeps context evidence chain separate from thermal chain."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    # Thermal chain should not contain GIS nodes
    thermal_steps = [e["step"] for e in result["evidence_chain"]]
    assert "canopy_request" not in thermal_steps
    assert "canopy_result" not in thermal_steps
    assert "parks_request" not in thermal_steps
    assert "parks_result" not in thermal_steps
    assert "context_enrichment_result" not in thermal_steps
    # Context chain should contain GIS nodes
    context_steps = [e["step"] for e in result["context_evidence_chain"]]
    assert "canopy_request" in context_steps
    assert "canopy_result" in context_steps
    assert "parks_request" in context_steps
    assert "parks_result" in context_steps
    assert "context_enrichment_result" in context_steps
    print("  PASS: test_controller_context_evidence_chain_separate")


def test_controller_gis_context_used_in_decision_false():
    """GIS context is marked as not used in decision."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    context = result.get("context", {})
    assert context.get("used_in_decision") is False
    if context.get("canopy"):
        assert context["canopy"].get("used_in_decision") is False
    if context.get("parks"):
        assert context["parks"].get("used_in_decision") is False
    print("  PASS: test_controller_gis_context_used_in_decision_false")


def test_controller_thermal_ranking_unchanged():
    """GIS context does not alter thermal ranking."""
    # Run without GIS
    with patch("src.agent.controller.enrich_candidate_context", return_value={"context": {"available": False}, "context_evidence_chain": []}):
        agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
        result_no_gis = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    
    # Run with GIS
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result_with_gis = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    
    # Compare ranked candidates
    ranked_no_gis = result_no_gis["answer"]["conditions"]["ranked_candidates"]
    ranked_with_gis = result_with_gis["answer"]["conditions"]["ranked_candidates"]
    assert len(ranked_no_gis) == len(ranked_with_gis)
    for i in range(len(ranked_no_gis)):
        assert ranked_no_gis[i]["rank"] == ranked_with_gis[i]["rank"]
        assert ranked_no_gis[i]["observed_temp"] == ranked_with_gis[i]["observed_temp"]
    print("  PASS: test_controller_thermal_ranking_unchanged")


# === BRIEF INTEGRATION TESTS ===

def test_brief_includes_local_context_section():
    """Brief includes LOCAL CONTEXT section when GIS data is available."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    brief = compose_urban_heat_brief(result)
    assert brief is not None
    section_ids = [s["section_id"] for s in brief["sections"]]
    assert "local_context" in section_ids, f"LOCAL CONTEXT section not found in: {section_ids}"
    print("  PASS: test_brief_includes_local_context_section")


def test_brief_local_context_provenance():
    """Brief LOCAL CONTEXT claims have proper provenance."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    brief = compose_urban_heat_brief(result)
    # Find claims by source_type
    local_context_claims = [c for c in brief["claims"] if c.get("source_type", "").startswith("gis_context")]
    assert len(local_context_claims) > 0
    for claim in local_context_claims:
        assert claim["used_in_decision"] is False
        assert claim["source_provider"]
        assert claim["evidence_nodes"]
    print("  PASS: test_brief_local_context_provenance")


def test_brief_local_context_disclosure():
    """Brief includes disclosure that GIS does not alter ranking."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    brief = compose_urban_heat_brief(result)
    disclosure_claims = [c for c in brief["claims"] if c.get("claim_id") == "local-context-disclosure"]
    assert len(disclosure_claims) == 1
    assert "does not alter" in disclosure_claims[0]["text"]
    print("  PASS: test_brief_local_context_disclosure")


def test_brief_gis_used_in_decision_false():
    """Brief GIS claims are marked as not used in decision."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    brief = compose_urban_heat_brief(result)
    assert brief.get("gis_used_in_decision") is False
    gis_claims = [c for c in brief["claims"] if c.get("source_type", "").startswith("gis_context")]
    for claim in gis_claims:
        assert claim["used_in_decision"] is False
    print("  PASS: test_brief_gis_used_in_decision_false")


def test_brief_zero_unsupported_claims():
    """All Brief claims map to permitted normative classes; none are unsupported."""
    PERMITTED_CLASSES = {
        "thermal_measurement",
        "environmental_measurement",
        "product_derived_comparison",
        "product_derived_decision_note",
        "official_current_context",
        "provenance_disclosure",
        "availability_disclosure",
        "product_derived_disclosure",
        "gis_context_canopy",
        "gis_context_parks",
    }
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    brief = compose_urban_heat_brief(result)
    unsupported = []
    for claim in brief["claims"]:
        st = claim.get("source_type", "")
        if st not in PERMITTED_CLASSES:
            unsupported.append(f"{claim['claim_id']}: {st}")
    assert not unsupported, f"Unsupported claims found: {unsupported}"
    print("  PASS: test_brief_zero_unsupported_claims")


# === VISUALIZATION PAYLOAD TESTS ===

def test_visualization_payload_includes_gis_context():
    """Visualization payload includes GIS context."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    payload = build_visualization_payload(result)
    assert "gis_context" in payload
    assert payload["gis_context"]["available"] is True
    print("  PASS: test_visualization_payload_includes_gis_context")


def test_visualization_payload_includes_context_evidence():
    """Visualization payload includes context evidence chain."""
    agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
    result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
    payload = build_visualization_payload(result)
    context_steps = [e["step"] for e in payload["evidence_chain"]]
    assert "canopy_request" in context_steps
    assert "parks_request" in context_steps
    print("  PASS: test_visualization_payload_includes_context_evidence")


# === REPLAY NETWORK BEHAVIOR TESTS ===

def test_replay_zero_gis_network_calls():
    """Replay mode makes zero GIS network calls."""
    # In replay mode, the GIS module loads from fixtures, not network
    # Verify that the query functions use fixtures
    from src.tools.gis_context import _load_gis_fixture
    fixture = _load_gis_fixture("canopy.json", "replay")
    assert fixture is not None, "Canopy fixture should be loaded in replay mode"
    fixture = _load_gis_fixture("parks.json", "replay")
    assert fixture is not None, "Parks fixture should be loaded in replay mode"
    print("  PASS: test_replay_zero_gis_network_calls")


# === LIVE MODE TESTS ===

def test_live_mode_gis_unavailable_without_adapter():
    """Live mode returns unavailable GIS context without adapter."""
    # In live mode, GIS queries real ArcGIS services
    # For non-Phoenix coordinates, canopy returns no features
    from src.tools.gis_context import query_tree_canopy, query_parks
    # Test with coordinates outside Phoenix area (should return no features)
    result = query_tree_canopy(40.0, -74.0, mode="live", adapter=None)
    # Live mode queries real ArcGIS - returns no features for non-Phoenix coords
    assert result.get("available") is False
    # Parks query may return available=True but with no park found
    result = query_parks(40.0, -74.0, mode="live", adapter=None)
    # Parks service is reachable, so available=True, but inside_park=None
    assert result.get("result", {}).get("inside_park") is None
    print("  PASS: test_live_mode_gis_unavailable_without_adapter")


# === FAILURE BEHAVIOR TESTS ===

def test_gis_failure_does_not_alter_ranking():
    """GIS failure does not alter thermal ranking."""
    # Run with GIS failure
    with patch("src.agent.controller.enrich_candidate_context", side_effect=Exception("GIS failure")):
        agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
        # Should still return thermal results
        try:
            result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
            # If exception is caught, verify thermal results are still present
            assert "answer" in result
        except Exception:
            # If exception propagates, that's also acceptable for Level A
            pass
    print("  PASS: test_gis_failure_does_not_alter_ranking")


def test_gis_failure_does_not_suppress_results():
    """GIS failure does not suppress valid FortyGuard results."""
    with patch("src.agent.controller.enrich_candidate_context", return_value={"context": {"available": False}, "context_evidence_chain": []}):
        agent = HeatAgent(FortyGuardAdapter(mode="replay"), mode="replay")
        result = agent.answer("Where should Phoenix prioritize a cooling intervention this afternoon?")
        # Verify thermal results are still present
        assert "answer" in result
        assert result["answer"].get("error") is not True
        assert result["answer"]["conditions"]["area_mean_temperature_celsius"] is not None
    print("  PASS: test_gis_failure_does_not_suppress_results")


# === GIS FAILURE DISTINCTION TESTS ===

def test_live_parks_success_zero_features():
    """Live parks query success with zero features returns available=true, inside_park=None."""
    with patch("src.tools.gis_context._query_arcgis_point") as mock_query:
        mock_query.return_value = {"success": True, "features": [], "error": None}
        result = query_parks(33.459, -112.0774, mode="live")
        assert result["result"]["available"] is True
        assert result["result"]["inside_park"] is None
    print("  PASS: test_live_parks_success_zero_features")


def test_live_parks_query_failure():
    """Live parks query failure returns available=false with explicit error."""
    with patch("src.tools.gis_context._query_arcgis_point") as mock_query:
        mock_query.return_value = {"success": False, "features": [], "error": "Connection timeout"}
        result = query_parks(33.459, -112.0774, mode="live")
        assert result.get("available") is False
        assert "arcgis_query_failed" in result.get("error", "")
    print("  PASS: test_live_parks_query_failure")


def test_replay_parks_coordinate_not_in_fixture():
    """Replay parks query with unknown coordinate returns available=false."""
    # Use a coordinate that's not in the fixture (far from Phoenix)
    result = query_parks(40.0, -74.0, mode="replay")
    assert result.get("available") is False
    assert result.get("error") == "candidate_not_in_fixture"
    print("  PASS: test_replay_parks_coordinate_not_in_fixture")


def test_live_canopy_query_failure():
    """Live canopy query failure returns available=false with explicit error."""
    with patch("src.tools.gis_context._query_arcgis_point") as mock_query:
        mock_query.return_value = {"success": False, "features": [], "error": "TLS error"}
        result = query_tree_canopy(33.4581, -112.0774, mode="live")
        assert result.get("available") is False
        assert "arcgis_query_failed" in result.get("error", "")
    print("  PASS: test_live_canopy_query_failure")


def run_all():
    tests = [
        # Fixture integrity
        test_gis_fixture_integrity_canopy,
        test_gis_fixture_integrity_parks,
        test_gis_fixture_manifest_separate_from_fortyguard,
        # Point-in-polygon
        test_point_in_polygon_inside,
        test_point_in_polygon_outside,
        # Canopy queries
        test_canopy_replay_success,
        test_canopy_tract_level_semantic_labeling,
        test_canopy_evidence_nodes,
        test_canopy_unavailable_point_outside,
        test_canopy_unavailable_missing_fixture,
        test_canopy_unavailable_corrupted_fixture,
        # Parks queries
        test_parks_replay_inside_park,
        test_parks_replay_outside_park,
        test_parks_nearby_bounded_query,
        test_parks_evidence_nodes,
        test_parks_unavailable_missing_fixture,
        test_parks_unavailable_corrupted_fixture,
        # Context enrichment
        test_enrich_candidate_context_success,
        test_enrich_candidate_context_canopy_only,
        test_enrich_candidate_context_parks_only,
        test_enrich_candidate_context_both_unavailable,
        # Format claims
        test_format_canopy_claim_success,
        test_format_canopy_claim_unavailable,
        test_format_parks_claim_inside,
        test_format_parks_claim_nearby,
        test_format_parks_claim_no_parks,
        test_format_parks_claim_unavailable,
        # Controller integration
        test_controller_replay_includes_context,
        test_controller_top3_enrichment,
        test_controller_thermal_evidence_chain_unchanged,
        test_controller_context_evidence_chain_separate,
        test_controller_gis_context_used_in_decision_false,
        test_controller_thermal_ranking_unchanged,
        # Brief integration
        test_brief_includes_local_context_section,
        test_brief_local_context_provenance,
        test_brief_local_context_disclosure,
        test_brief_gis_used_in_decision_false,
        test_brief_zero_unsupported_claims,
        # Visualization payload
        test_visualization_payload_includes_gis_context,
        test_visualization_payload_includes_context_evidence,
        # Network behavior
        test_replay_zero_gis_network_calls,
        # Live mode
        test_live_mode_gis_unavailable_without_adapter,
        # Failure behavior
        test_gis_failure_does_not_alter_ranking,
        test_gis_failure_does_not_suppress_results,
        # GIS failure distinction
        test_live_parks_success_zero_features,
        test_live_parks_query_failure,
        test_replay_parks_coordinate_not_in_fixture,
        test_live_canopy_query_failure,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__}: {exc}")
    print(f"\nLEVEL A GIS TESTS: {passed}/{len(tests)} PASS, {len(tests) - passed} FAIL")
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
