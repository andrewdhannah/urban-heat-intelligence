# R6-R1 Remediation Receipt

**Branch:** `remediation/dash-v2-r6-r1-closure`
**Parent SHA:** `c4900eef3a33354e986e7a3c7fd1c67f6ca1f31b` (R6 receipt)
**Date:** 2026-08-29
**Agent:** opencode-go/mimo-v2.5

## R6 Receipt Overstatements Corrected

Owner review of the pushed R6 SHA found the following receipt overstatements:

1. **R6 intersection report stated Haversine distance** although R6 code did not implement Haversine. R6 relied on ArcGIS `returnDistance=true` and a `dist`/`distance` attribute fallback. R6-R1 implements actual Haversine computation from authoritative returned WGS84 geometry.

2. **R6 receipt listed controller.py as changed** for obligation 9 (Live intersection enrichment) although the R6 implementation commit did not modify controller.py. R6-R1 corrects this attribution.

3. **R6 browser matrix was structural verification**, not full visual browser proof. R6-R1 supplements with executable tests; full visual proof remains pending manual inspection.

4. **R6 verification recorded only additive test accounting**, not the required full regression accounting. R6-R1 provides full regression results.

## Defects Closed

| ID | Defect | Closure |
|----|--------|---------|
| R6-R1-001 | Static-asset handler sent double HTTP response headers | `serve_versioned_asset()` reads file and writes single response; index gets `Cache-Control: no-cache` |
| R6-R1-002 | Intersection endpoint used wrong ArcGIS service and wrong fields | Replaced with authoritative `Public/STR_StreetIntersections/MapServer/0`; fields: INTERSECTION, DIR1, STREET1, DIR2, STREET2 |
| R6-R1-003 | R6 claimed Haversine but relied on ArcGIS distance attribute | `_haversine_distance()` implemented; distance_method recorded as `haversine_from_authoritative_returned_geometry` |
| R6-R1-004 | Intersection failure had no explicit consumer wording | Added distinct states: provider failure, no intersection within 200m, location unavailable |
| R6-R1-005 | focusCandidate only panned, did not zoom | Changed to `flyTo(..., 16, ...)` for neighborhood-scale zoom on candidate selection |
| R6-R1-006 | Tests used source-string assertions; no mocked intersection success | 26 new tests with mocked ArcGIS responses, Haversine verification, real HTTP handler proof |
| R6-R1-007 | Only additive test accounting reported | Full regression: 233 collected, 232 passed, 0 failed, 1 environment-blocked |

## Files Changed

| File | Changes |
|------|---------|
| `app/server.py` | `serve_versioned_asset()` for single-response versioned delivery; index no-cache; build version from `RENDER_GIT_COMMIT` |
| `src/tools/gis_context.py` | Authoritative intersection endpoint; `_haversine_distance()`; WGS84 geometry distance; distinct failure states |
| `app/dashboard-luna/js/dashboard.js` | `focusCandidate()` uses `flyTo` for neighborhood zoom; intersection unavailable shows "Location context unavailable" |
| `fixtures/phoenix-gis/parks.json` | Updated coordinates to match Shoelace centroids; added test-coordinate entries |
| `fixtures/phoenix-gis/integrity-manifest.json` | Updated parks fixture hash |
| `tests/test_r6_r1_closure.py` | 26 new tests: static asset HTTP proof, centroid variants, ranking preservation, intersection success/failure/mock, replay isolation, focus zoom |

## Verification

### Full Regression Suite
```
total_collected: 233
passed: 232
failed: 0
skipped: 0
environment_blocked: 1 (test_env_key_consumed_server_side — requires FORTYGUARD_API_KEY)
```

### R6-R1 Additive Tests
```
collected: 26
passed: 26
failed: 0
```

### R6 Additive Tests (preserved)
```
collected: 21
passed: 21
failed: 0
```

## Invariants Preserved

- FortyGuard = ranking evidence
- NWS = supplemental context, not ranking
- Phoenix GIS = local context, not ranking
- Intersection = local context, `used_in_decision=false`
- Replay ≠ Live
- No credentials in browser payload, source, logs, test output, or receipt
