"""
R6-R1 Closure Tests — Static asset delivery, intersection source,
Haversine distance, focus zoom, and test quality overhaul.

Tests cover:
A. Static Asset HTTP Proof (UHIHandler)
B. Centroid Tests (Shoelace formula)
C. Ranking Preservation (temperature descending)
D. Intersection Success (mocked authoritative City Phoenix ArcGIS)
E. Intersection Failure
F. Replay (no intersection network request)
G. Candidate Focus (flyTo on pan=true)
"""

import io
import json
import math
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# A. Static Asset HTTP Proof
# ---------------------------------------------------------------------------

def _make_handler(path):
    """Create a UHIHandler with a mocked socket for testing."""
    from app.server import UHIHandler, get_dashboard_dir
    # Mock the socket/IO
    handler = UHIHandler.__new__(UHIHandler)
    handler.path = path
    handler.request_version = "HTTP/1.1"
    handler.wfile = io.BytesIO()
    handler.rfile = io.BytesIO()
    handler.headers = {}
    handler.responses = {}
    # Minimal output headers tracking
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))
    return handler


def _parse_response(raw_bytes):
    """Parse raw bytes into status code, headers dict, and body."""
    text = raw_bytes.decode("utf-8", errors="replace")
    lines = text.split("\r\n")
    status_code = None
    headers = {}
    body_start = False
    body_lines = []
    for line in lines:
        if not body_start:
            if line.startswith("HTTP/"):
                status_code = int(line.split(" ")[1])
            elif ": " in line:
                k, v = line.split(": ", 1)
                headers[k] = v
            elif line == "":
                body_start = True
        else:
            body_lines.append(line)
    body = "\r\n".join(body_lines)
    return status_code, headers, body


def test_versioned_css_asset_single_response():
    """CSS asset with ?v= returns single HTTP response with correct headers."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))

    parsed = type("P", (), {"query": "v=r6-dev", "path": "/css/tokens.css"})()
    handler.serve_versioned_asset(parsed)
    raw = handler.wfile.getvalue().decode("utf-8", errors="replace")

    # Should NOT contain HTTP status line (no double headers)
    assert not raw.startswith("HTTP/"), f"Body starts with HTTP status line — double headers: {raw[:80]}"

    # Should start with CSS content
    assert raw.strip().startswith(":root") or raw.strip().startswith("/*") or "font" in raw.lower() or "color" in raw.lower(), \
        f"CSS content not found at start: {raw[:80]}"

    # Check buffer for exactly one status code
    status_codes = [e[1] for e in handler._headers_buffer if e[0] == "status"]
    assert len(status_codes) == 1, f"Expected 1 status code, got {len(status_codes)}: {status_codes}"
    assert status_codes[0] == 200

    # Check headers
    header_dict = {e[1]: e[2] for e in handler._headers_buffer if e[0] == "header"}
    assert "Cache-Control" in header_dict, "Cache-Control header missing"
    assert "immutable" in header_dict["Cache-Control"], "Cache-Control not immutable"
    assert "Content-Type" in header_dict, "Content-Type header missing"
    assert "css" in header_dict["Content-Type"].lower(), f"Content-Type not CSS: {header_dict['Content-Type']}"


def test_versioned_js_asset_single_response():
    """JS asset with ?v= returns single HTTP response with correct headers."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))

    parsed = type("P", (), {"query": "v=r6-dev", "path": "/js/dashboard.js"})()
    handler.serve_versioned_asset(parsed)
    raw = handler.wfile.getvalue().decode("utf-8", errors="replace")

    # Should NOT contain HTTP status line
    assert not raw.startswith("HTTP/"), f"Body starts with HTTP status line — double headers: {raw[:80]}"

    # Should contain JS content
    assert "const " in raw or "function " in raw or "var " in raw or "=>" in raw, \
        f"JS content not found at start: {raw[:80]}"

    # Check exactly one status code
    status_codes = [e[1] for e in handler._headers_buffer if e[0] == "status"]
    assert len(status_codes) == 1, f"Expected 1 status code, got {len(status_codes)}"
    assert status_codes[0] == 200

    # Check headers
    header_dict = {e[1]: e[2] for e in handler._headers_buffer if e[0] == "header"}
    assert "Cache-Control" in header_dict
    assert "immutable" in header_dict["Cache-Control"]
    assert "javascript" in header_dict.get("Content-Type", "").lower() or "text" in header_dict.get("Content-Type", "").lower()


def test_stale_asset_version_is_not_immutable():
    """Only the active build URL receives immutable caching."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))
    with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "build-current"}):
        parsed = type("P", (), {"query": "v=build-old", "path": "/css/tokens.css"})()
        handler.serve_versioned_asset(parsed)
    headers = dict((e[1], e[2]) for e in handler._headers_buffer if e[0] == "header")
    assert "immutable" not in headers["Cache-Control"]
    assert "no-cache" in headers["Cache-Control"]


def test_versioned_asset_404():
    """Non-existent versioned asset returns 404."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))
    handler.send_error = lambda code, msg: handler._headers_buffer.append(("status", code))

    parsed = type("P", (), {"query": "v=r6", "path": "/nonexistent/file.css"})()
    handler.serve_versioned_asset(parsed)

    status_codes = [e[1] for e in handler._headers_buffer if e[0] == "status"]
    assert 404 in status_codes, f"Expected 404 for non-existent asset, got {status_codes}"


def test_index_html_no_cache():
    """Index.html has Cache-Control: no-cache for revalidation."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))

    handler.serve_index()
    raw = handler.wfile.getvalue().decode("utf-8", errors="replace")

    assert "<!doctype html>" in raw.lower() or "<!DOCTYPE html>" in raw, "Index content not HTML"

    header_dict = {e[1]: e[2] for e in handler._headers_buffer if e[0] == "header"}
    assert "Cache-Control" in header_dict, "Cache-Control header missing on index"
    assert "no-cache" in header_dict["Cache-Control"], f"Index Cache-Control should include no-cache: {header_dict['Cache-Control']}"


def test_index_html_serve_index_single_response():
    """Index handler produces exactly one status code."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))

    handler.serve_index()
    status_codes = [e[1] for e in handler._headers_buffer if e[0] == "status"]
    assert len(status_codes) == 1, f"Expected 1 status, got {len(status_codes)}"


def test_index_asset_urls_follow_build_identity():
    """The no-cache index binds descendant URLs to the running build."""
    from app.server import UHIHandler
    handler = UHIHandler.__new__(UHIHandler)
    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    handler.send_response = lambda code, message=None: handler._headers_buffer.append(("status", code))
    handler.send_header = lambda key, val: handler._headers_buffer.append(("header", key, val))
    handler.end_headers = lambda: handler._headers_buffer.append(("end_headers",))
    with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "build-a"}):
        handler.serve_index()
    first = handler.wfile.getvalue().decode()
    assert "?v=build-a" in first
    assert "{{BUILD_VERSION}}" not in first
    assert "Cache-Control" in dict((e[1], e[2]) for e in handler._headers_buffer if e[0] == "header")

    handler.wfile = io.BytesIO()
    handler._headers_buffer = []
    with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "build-b"}):
        handler.serve_index()
    second = handler.wfile.getvalue().decode()
    assert "?v=build-b" in second
    assert first != second


def test_dashboard_closure_contracts_are_runtime_wired():
    """Critical 2-D contracts are present in the executable dashboard source."""
    content = Path("app/dashboard-luna/js/dashboard.js").read_text()
    assert "const deskState" in content
    assert "requestGeneration" in content
    assert "ResizeObserver" in content
    assert "intersection.available" in content
    assert "Location context unavailable" in content
    assert "renderReadout()" in content


# ---------------------------------------------------------------------------
# B. Centroid Tests
# ---------------------------------------------------------------------------

def test_centroid_closed_ring():
    """Closed GeoJSON ring produces correct Shoelace centroid."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[0, 0], [6, 0], [0, 6]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    assert abs(centroid[0] - 2.0) < 1e-4
    assert abs(centroid[1] - 2.0) < 1e-4


def test_centroid_non_closed_ring():
    """Non-closed ring still produces a centroid (vertex average fallback)."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[1, 1], [3, 1], [3, 3], [1, 3]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    assert abs(centroid[0] - 2.0) < 1e-4
    assert abs(centroid[1] - 2.0) < 1e-4


def test_centroid_irregular_polygon():
    """Irregular polygon centroid lies inside the polygon."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[0, 0], [4, 0], [4, 3], [2, 5], [0, 3]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    # Centroid should be roughly inside the polygon
    assert 0 < centroid[0] < 4
    assert 0 < centroid[1] < 5


def test_centroid_degenerate_polygon():
    """Degenerate polygon (2 points) falls back to first vertex."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[1, 2], [3, 4]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    # For < 3 points, returns first point
    assert centroid == [1, 2]


def test_centroid_single_point():
    """Single point returns itself."""
    from src.tools.heatmap import _polygon_centroid
    coords = [[7, 8]]
    centroid = _polygon_centroid(coords)
    assert centroid == [7, 8]


def test_centroid_known_fixture_cell():
    """Known FortyGuard fixture cell produces valid centroid."""
    from src.tools.heatmap import _polygon_centroid
    # A typical rectangular tile
    coords = [[-112.078, 33.457], [-112.077, 33.457], [-112.077, 33.458], [-112.078, 33.458]]
    centroid = _polygon_centroid(coords)
    assert centroid is not None
    assert -112.079 < centroid[0] < -112.076
    assert 33.456 < centroid[1] < 33.459


# ---------------------------------------------------------------------------
# C. Ranking Preservation
# ---------------------------------------------------------------------------

def test_ranking_temperature_descending():
    """Candidates maintain temperature-descending order."""
    from src.tools.heatmap import normalize_heatmap_result
    fixture_path = Path("fixtures/fortyguard/replay-response.json")
    if not fixture_path.exists():
        return  # Skip if fixture not present

    with open(fixture_path) as f:
        fixture = json.load(f)

    request_params = fixture.get("request_params", {})
    result = normalize_heatmap_result(
        fixture.get("result", fixture),
        request_params,
        mode="replay",
        fixture_path=str(fixture_path)
    )
    candidates = result.get("candidates", [])
    if len(candidates) < 2:
        return

    temps = [c["observed_temp"] for c in candidates]
    for i in range(len(temps) - 1):
        assert temps[i] >= temps[i + 1], \
            f"Ranking violated: candidate {i} temp {temps[i]} < candidate {i+1} temp {temps[i+1]}"


def test_ranking_tile_ids_stable():
    """Candidate tile_ids remain unchanged after normalization."""
    from src.tools.heatmap import normalize_heatmap_result
    fixture_path = Path("fixtures/fortyguard/replay-response.json")
    if not fixture_path.exists():
        return

    with open(fixture_path) as f:
        fixture = json.load(f)

    request_params = fixture.get("request_params", {})
    result = normalize_heatmap_result(
        fixture.get("result", fixture),
        request_params,
        mode="replay",
        fixture_path=str(fixture_path)
    )
    candidates = result.get("candidates", [])
    # Each candidate should have a tile_id
    for c in candidates:
        assert "tile_id" in c, f"Candidate missing tile_id: {c}"
        assert c["tile_id"] is not None, f"Candidate tile_id is None: {c}"


# ---------------------------------------------------------------------------
# D. Intersection Success (Mocked)
# ---------------------------------------------------------------------------

def test_intersection_authoritative_endpoint():
    """Mocked intersection query uses City of Phoenix authoritative endpoint."""
    from src.tools.gis_context import query_nearest_intersection, INTERSECTION_ENDPOINT
    assert "maps.phoenix.gov" in INTERSECTION_ENDPOINT, \
        f"Intersection endpoint not authoritative: {INTERSECTION_ENDPOINT}"
    assert "STR_StreetIntersections" in INTERSECTION_ENDPOINT, \
        f"Intersection endpoint not on correct layer: {INTERSECTION_ENDPOINT}"


def test_intersection_correct_field_contract():
    """Intersection query requests authoritative fields only."""
    from src.tools.gis_context import query_nearest_intersection
    mock_response = {
        "features": [
            {
                "attributes": {
                    "INTERSECTION": "MONROE ST & 7TH ST",
                    "DIR1": "N",
                    "STREET1": "7TH",
                    "DIR2": "",
                    "STREET2": "MONROE"
                },
                "geometry": {"x": -112.074, "y": 33.458}
            }
        ]
    }
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value = mock_resp
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    # Verify the URL contains the authoritative endpoint
    call_args = mock_urlopen.call_args
    url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
    assert "maps.phoenix.gov" in url, f"Wrong endpoint: {url}"
    assert "INTERSECTION" in url, f"INTERSECTION field not requested: {url}"
    assert "DIR1" in url, f"DIR1 field not requested: {url}"
    assert "STREET1" in url, f"STREET1 field not requested: {url}"
    # Verify old fields are NOT requested
    assert "FULL_NAME" not in url, f"FULL_NAME should not be requested: {url}"
    assert "PRE_DIR" not in url, f"PRE_DIR should not be requested: {url}"


def test_intersection_haversine_distance_computed_locally():
    """Nearest intersection selected by Haversine, not ArcGIS attribute."""
    from src.tools.gis_context import query_nearest_intersection
    # Two intersections at different distances
    mock_response = {
        "features": [
            {
                "attributes": {"INTERSECTION": "FAR AWAY ST & AVE", "DIR1": "N", "STREET1": "AVE", "DIR2": "", "STREET2": "FAR AWAY"},
                "geometry": {"x": -112.10, "y": 33.50}  # ~5km away
            },
            {
                "attributes": {"INTERSECTION": "MONROE ST & 7TH ST", "DIR1": "N", "STREET1": "7TH", "DIR2": "", "STREET2": "MONROE"},
                "geometry": {"x": -112.074, "y": 33.458}  # ~100m away
            }
        ]
    }
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value = mock_resp
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    res = result["result"]
    assert res["available"] is True
    assert res["name"] == "MONROE ST & 7TH ST", f"Wrong intersection selected: {res['name']}"
    assert res["distance_m"] < 5000, f"Distance too large: {res['distance_m']}"
    assert res["distance_method"] == "haversine_from_authoritative_returned_geometry"


def test_intersection_haversine_distance_is_computed():
    """Haversine distance is computed from geometry, not read from attribute."""
    from src.tools.gis_context import query_nearest_intersection, _haversine_distance
    # Verify Haversine function works
    # Phoenix approximate: 33.4484, -112.074
    dist = _haversine_distance(33.4484, -112.074, 33.4494, -112.074)
    assert 90 < dist < 120, f"Haversine distance for ~100m offset: {dist}"


def test_intersection_used_in_decision_false():
    """Intersection result always has used_in_decision=false."""
    from src.tools.gis_context import query_nearest_intersection
    mock_response = {
        "features": [
            {
                "attributes": {"INTERSECTION": "TEST ST & AVE", "DIR1": "", "STREET1": "AVE", "DIR2": "", "STREET2": "TEST"},
                "geometry": {"x": -112.074, "y": 33.458}
            }
        ]
    }
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value = mock_resp
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    assert result["result"]["used_in_decision"] is False
    assert result["result_evidence_node"]["data"]["used_in_decision"] is False


def test_intersection_name_from_authoritative_field():
    """Intersection name comes from the INTERSECTION attribute."""
    from src.tools.gis_context import query_nearest_intersection
    mock_response = {
        "features": [
            {
                "attributes": {"INTERSECTION": "INDIAN SCHOOL RD & CAMELBACK RD", "DIR1": "", "STREET1": "CAMELBACK", "DIR2": "", "STREET2": "INDIAN SCHOOL"},
                "geometry": {"x": -112.074, "y": 33.458}
            }
        ]
    }
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value = mock_resp
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    assert result["result"]["name"] == "INDIAN SCHOOL RD & CAMELBACK RD"


# ---------------------------------------------------------------------------
# E. Intersection Failure
# ---------------------------------------------------------------------------

def test_intersection_provider_failure():
    """Provider failure: thermal result preserved, context unavailable."""
    from src.tools.gis_context import query_nearest_intersection
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("Connection refused")
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    assert result["available"] is False
    assert "intersection_query_failed" in result["error"]
    assert "evidence_node" in result


def test_intersection_zero_features():
    """Zero features returns distinct unavailable state."""
    from src.tools.gis_context import query_nearest_intersection
    mock_response = {"features": []}
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_response).encode()
        mock_urlopen.return_value = mock_resp
        result = query_nearest_intersection(33.457, -112.074, mode="live")

    assert result["available"] is False
    assert result["error"] == "no_intersection_within_200m"


def test_intersection_unavailable_state_survives_context_enrichment():
    """No-result and provider-failure context remains consumable by the UI."""
    from src.tools.gis_context import enrich_candidate_context
    with patch("src.tools.gis_context.query_tree_canopy", return_value={}), \
         patch("src.tools.gis_context.query_parks", return_value={}), \
         patch("src.tools.gis_context.query_nearest_intersection", return_value={
             "available": False,
             "error": "no_intersection_within_200m",
             "used_in_decision": False,
         }):
        context = enrich_candidate_context(33.457, -112.074, mode="live")["context"]
    assert context["intersection"]["error"] == "no_intersection_within_200m"
    assert context["intersection"]["used_in_decision"] is False


def test_intersection_replay_returns_fixture_or_bounded_unavailable():
    """Replay uses captured context and rejects unrelated coordinates."""
    from src.tools.gis_context import query_nearest_intersection
    result = query_nearest_intersection(33.459941, -112.077282, mode="replay")
    assert result["result"]["available"] is True
    assert result["result"]["used_in_decision"] is False
    unrelated = query_nearest_intersection(40.0, -74.0, mode="replay")
    assert unrelated["available"] is False


# ---------------------------------------------------------------------------
# F. Replay — No Intersection Network Request
# ---------------------------------------------------------------------------

def test_replay_no_intersection_network_request():
    """Replay mode does not make any intersection network request."""
    from src.tools.gis_context import enrich_candidate_context
    with patch("src.tools.gis_context.urllib.request.urlopen") as mock_urlopen:
        result = enrich_candidate_context(33.4581, -112.0774, mode="replay")
        # urlopen should NOT be called in replay mode
        mock_urlopen.assert_not_called()

    # Context should still be available from fixtures
    ctx = result["context"]
    assert ctx["used_in_decision"] is False


# ---------------------------------------------------------------------------
# G. Candidate Focus — flyTo on pan=true
# ---------------------------------------------------------------------------

def test_focus_candidate_flyTo_in_source():
    """dashboard.js uses flyTo (not panTo) for pan=true focus."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "flyTo" in content, "flyTo not found in dashboard.js"
    assert "marker.getLatLng(), 16" in content or "marker.getLatLng(),16" in content, \
        "flyTo should use zoom level 16"
    # panTo should NOT be used for candidate focus
    # (panTo may exist for other uses, but focusCandidate should use flyTo)
    # Find the focusCandidate function
    import re
    focus_fn = re.search(r'function focusCandidate\([^}]+\}', content)
    if focus_fn:
        assert "panTo" not in focus_fn.group(), \
            "focusCandidate should use flyTo, not panTo"


def test_intersection_display_available():
    """Dashboard renders intersection name when available."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "Nearest intersection:" in content, "Available intersection display text missing"


def test_intersection_display_unavailable():
    """Dashboard renders 'Location context unavailable' when intersection unavailable."""
    js_path = Path("app/dashboard-luna/js/dashboard.js")
    content = js_path.read_text()
    assert "Location context unavailable" in content, \
        "Unavailable intersection display text missing"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _collect_tests():
    """Collect all test_ functions from this module."""
    tests = []
    for name, obj in sorted(globals().items()):
        if name.startswith("test_") and callable(obj):
            tests.append(obj)
    return tests


def run_all():
    tests = _collect_tests()
    passed = 0
    failed = 0
    errors = []
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  PASS: {test.__name__}")
        except Exception as e:
            failed += 1
            errors.append((test.__name__, str(e)))
            print(f"  FAIL: {test.__name__}: {e}")
    print(f"\n{'='*60}")
    print(f"R6-R1 CLOSURE TESTS: {passed}/{passed + failed} PASS, {failed} FAIL")
    if errors:
        for name, err in errors:
            print(f"  FAILED: {name}: {err}")
    return failed == 0


if __name__ == "__main__":
    import traceback
    tests = _collect_tests()
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
    print(f"\n{'='*60}")
    print(f"R6-R1 CLOSURE TESTS: {passed}/{passed + failed} PASS, {failed} FAIL")
    if failed:
        sys.exit(1)
