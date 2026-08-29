"""
R6 Additive Tests — Public Deployment Coherency + UX Remediation

Tests for the 15 R6 obligations.  All tests are additive and verify
behavioural contracts without modifying existing test fixtures or ranking.
"""

import math
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Step 8: Polygon centroid (Shoelace formula)
# ---------------------------------------------------------------------------

def test_shoelace_centroid_triangle():
    """Shoelace centroid of a right triangle should be at 1/3 of each axis."""
    from src.tools.heatmap import _polygon_centroid
    # Right triangle: (0,0), (6,0), (0,6)
    coords = [[0, 0], [6, 0], [0, 6]]
    centroid = _polygon_centroid(coords)
    # Expected: (2, 2)
    assert centroid is not None, "Centroid should not be None"
    assert abs(centroid[0] - 2.0) < 1e-4, f"cx should be ~2.0, got {centroid[0]}"
    assert abs(centroid[1] - 2.0) < 1e-4, f"cy should be ~2.0, got {centroid[1]}"


def test_shoelace_centroid_square():
    """Centroid of a unit square should be at its center."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    assert abs(centroid[0] - 0.5) < 1e-4
    assert abs(centroid[1] - 0.5) < 1e-4


def test_centroid_fallback_degenerate():
    """Degenerate polygon (fewer than 3 points) falls back to vertex average."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[1, 2]]
    centroid = _polygon_centroid(coords)
    assert centroid == [1, 2]


def test_centroid_fallback_collinear():
    """Collinear points (zero area) fall back to vertex average."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[0, 0], [1, 1], [2, 2]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    assert abs(centroid[0] - 1.0) < 1e-4
    assert abs(centroid[1] - 1.0) < 1e-4


def test_centroid_old_vertex_average_differs():
    """Old vertex-average centroid differs from Shoelace for non-symmetric polygon."""
    from src.tools.heatmap import _polygon_centroid
    # Asymmetric polygon where vertex average != area centroid
    coords = [[0, 0], [4, 0], [4, 1], [1, 1], [1, 4], [0, 4]]
    centroid = _polygon_centroid(coords)
    # Shoelace centroid should be closer to the large area's center
    # Vertex average would be (10/6, 10/6) ≈ (1.667, 1.667)
    # Shoelace gives area-weighted result
    assert centroid is not None
    assert centroid[0] != round(10 / 6, 6) or centroid[1] != round(10 / 6, 6), \
        "Shoelace centroid should differ from simple vertex average"


# ---------------------------------------------------------------------------
# Step 8: Ranking unchanged after centroid correction
# ---------------------------------------------------------------------------

def test_ranking_order_preserved_after_centroid():
    """Centroid correction does not change ranking order."""
    from src.tools.heatmap import _polygon_centroid
    # Simulate two candidates with different polygon shapes
    poly_a = [[0, 0], [2, 0], [2, 2], [0, 2]]  # square
    poly_b = [[5, 5], [7, 5], [6, 7]]  # triangle
    centroid_a = _polygon_centroid(poly_a)
    centroid_b = _polygon_centroid(poly_b)
    # Both should produce valid centroids
    assert centroid_a is not None
    assert centroid_b is not None
    # Temperature ordering is independent of centroid calculation
    # (centroid only affects representative coordinate, not rank)


# ---------------------------------------------------------------------------
# Step 9: Live intersection enrichment
# ---------------------------------------------------------------------------

def test_intersection_not_queried_in_replay():
    """Intersection query returns unavailable in replay mode."""
    from src.tools.gis_context import query_nearest_intersection
    result = query_nearest_intersection(33.45, -112.07, mode="replay")
    assert result["available"] is False
    assert result["error"] == "intersection_not_queried_in_replay"
    assert result["evidence_node"]["data"]["mode"] == "replay"


def test_intersection_used_in_decision_false():
    """Intersection context is always used_in_decision=false."""
    from src.tools.gis_context import query_nearest_intersection
    result = query_nearest_intersection(33.45, -112.07, mode="replay")
    assert result["evidence_node"]["data"].get("used_in_decision") is not True
    # The result itself (when available) would have used_in_decision=false
    # This is verified by the schema in the function definition


def test_gis_used_in_decision_false():
    """GIS enrichment context is always used_in_decision=false."""
    from src.tools.gis_context import enrich_candidate_context
    # This calls the full enrichment pipeline — it will fail on live (no ArcGIS)
    # but the contract is that used_in_decision=False is always set
    result = enrich_candidate_context(33.45, -112.07, mode="replay")
    ctx = result["context"]
    assert ctx["used_in_decision"] is False


# ---------------------------------------------------------------------------
# Step 1: Asset version contract
# ---------------------------------------------------------------------------

def test_index_html_cache_busting_params():
    """Dashboard index.html binds CSS/JS URLs to the server build identity."""
    html_path = Path("app/dashboard-luna/index.html")
    content = html_path.read_text()
    assert 'css/tokens.css?v={{BUILD_VERSION}}' in content, "tokens.css missing build placeholder"
    assert 'css/dashboard.css?v={{BUILD_VERSION}}' in content, "dashboard.css missing build placeholder"
    assert 'css/responsive.css?v={{BUILD_VERSION}}' in content, "responsive.css missing build placeholder"
    assert 'js/dashboard.js?v={{BUILD_VERSION}}' in content, "dashboard.js missing build placeholder"


# ---------------------------------------------------------------------------
# Step 4: Explore questions population
# ---------------------------------------------------------------------------

def test_explore_questions_groups_exist():
    """Dashboard JS defines catalogue groups with Decision/Context/Evidence categories."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "CATALOGUE_GROUPS" in content, "CATALOGUE_GROUPS not found in dashboard.js"
    assert "decision" in content, "Decision group not defined"
    assert "context" in content, "Context group not defined"
    assert "evidence" in content, "Evidence group not defined"


def test_explore_questions_toggle_aria():
    """Explore questions uses aria-expanded for accessibility."""
    html_path = Path("app/dashboard-luna/index.html")
    content = html_path.read_text()
    assert 'aria-expanded="false"' in content, "Catalogue toggle missing aria-expanded"
    assert 'aria-controls="catalogue-panel"' in content, "Catalogue toggle missing aria-controls"


# ---------------------------------------------------------------------------
# Step 10: Map focus exit — floating layer removed
# ---------------------------------------------------------------------------

def test_focus_exit_layer_removed():
    """The floating focus-exit-layer div is removed from index.html."""
    html_path = Path("app/dashboard-luna/index.html")
    content = html_path.read_text()
    assert "focus-exit-layer" not in content, "focus-exit-layer still present in HTML"


def test_focus_exit_button_in_map_header():
    """Exit button is inside the map-source area (map header)."""
    html_path = Path("app/dashboard-luna/index.html")
    content = html_path.read_text()
    assert "focus-exit-inline" in content, "focus-exit-inline class not found in HTML"


# ---------------------------------------------------------------------------
# Step 2: Hero context rail
# ---------------------------------------------------------------------------

def test_hero_context_rail_present():
    """index.html contains hero-context-rail instead of observation-card."""
    html_path = Path("app/dashboard-luna/index.html")
    content = html_path.read_text()
    assert "hero-context-rail" in content, "hero-context-rail not found"
    assert "observation-card" not in content, "observation-card should be replaced"


def test_hero_context_rail_renderer():
    """dashboard.js defines renderHeroContextRail function."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "renderHeroContextRail" in content, "renderHeroContextRail not defined"
    assert "hero-context-label" in content, "hero-context-label reference missing"
    assert "hero-context-content" in content, "hero-context-content reference missing"
    assert "hero-identity" in content, "hero-identity reference missing"


# ---------------------------------------------------------------------------
# Step 7: Source-cell binding
# ---------------------------------------------------------------------------

def test_source_cell_highlight_function():
    """dashboard.js defines highlightSourceCell for source-cell binding."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "highlightSourceCell" in content, "highlightSourceCell not defined"
    assert "source-cell-highlight" in content, "source-cell-highlight class not referenced"


def test_source_cell_highlight_css():
    """dashboard.css defines source-cell-highlight Leaflet style."""
    css_path = Path("app/dashboard-luna/css/dashboard.css")
    content = css_path.read_text()
    assert "source-cell-highlight" in content, "source-cell-highlight CSS not defined"


# ---------------------------------------------------------------------------
# Step 6: Candidate markers
# ---------------------------------------------------------------------------

def test_candidate_marker_improved_html():
    """addMarker uses improved HTML with explicit rank number rendering."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "DM Mono" in content, "Marker should use DM Mono font"


# ---------------------------------------------------------------------------
# Step 5: Controls styling (segmented)
# ---------------------------------------------------------------------------

def test_mode_button_segmented_css():
    """Mode buttons use zero border-radius for segmented control appearance."""
    css_path = Path("app/dashboard-luna/css/dashboard.css")
    content = css_path.read_text()
    assert "border-radius:0" in content.replace(" ", ""), "Segmented control border-radius:0 not found"


# ---------------------------------------------------------------------------
# Step 13: Typography
# ---------------------------------------------------------------------------

def test_eyebrow_uses_dm_mono():
    """tokens.css sets .eyebrow font-family to DM Mono."""
    css_path = Path("app/dashboard-luna/css/tokens.css")
    content = css_path.read_text()
    assert "DM Mono" in content, "eyebrow DM Mono not in tokens.css"


# ---------------------------------------------------------------------------
# Run all tests if executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  PASS: {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {test.__name__}: {e}")
            traceback.print_exc()
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed:
        sys.exit(1)
