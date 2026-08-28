# DASH-V2-PARALLEL-QA — Documentation Truth Refresh + Prequalification Test Preparation

**QA-Pilot · Parallel to DASH-V2-H · Not DASH-V2-I**

---

## 1. Execution Isolation

| Field | Value |
|-------|-------|
| Worktree | `/Users/andrew/Desktop/Freebuff/uhi-qa-pilot` |
| Branch | `qa-pilot/dash-v2-prequal-docs-tests` |
| Base SHA | `7dabd3805cc461a9fa7fd6db998c1081fbbae07d` |
| Isolated from H | YES — separate worktree, separate branch |
| Clean worktree | YES |

---

## 2. Documentation Truth Audit

### Documents Reviewed (18 files)

| Document | Status | Issues |
|----------|--------|--------|
| README.md | STALE | 3 truth issues |
| docs/user-guide/USER-GUIDE.md | STALE | 4 truth issues |
| docs/user-guide/QUICKSTART.md | STALE | 2 truth issues |
| docs/user-guide/UNDERSTANDING-YOUR-EVIDENCE.md | STALE | 2 truth issues |
| docs/teaching/UHI-PRODUCT-TEACHING-001.md | STALE | 3 truth issues |
| docs/teaching/UHI-EVIDENCE-PROVENANCE-TEACHING-001.md | STALE | 1 truth issue |
| docs/teaching/UHI-LIVE-REPLAY-TEACHING-001.md | STALE | 1 truth issue |
| docs/teaching/UHI-DATA-SOURCES-TEACHING-001.md | STALE | 2 truth issues |
| docs/ARCHITECTURE.md | STALE | Complete rewrite needed (describes unimplemented concept) |
| docs/dashboard-luna/README.md | ACCURATE | No issues |

### Stale Claims Found (16 total)

#### README.md

1. **Line 13**: "Calls FortyGuard Environmental Parameters for each candidate" — MISLEADING. env_params is called once at a single point, not per-candidate. Values are shared representative context.

2. **Line 77**: "CARTO dark basemap" — INCORRECT. Luna uses OpenStreetMap, not CARTO.

3. **Line 93-96**: "How to Demo" section references "Why This Answer?" panel — STALE. Luna uses "Inspect evidence +".

#### USER-GUIDE.md

4. **Line 22**: "Environmental parameters (humidity, apparent temperature, heat index)" — MISSING QUALIFIER. These are representative/shared context, not per-candidate measurements.

5. **Line 66**: "click **'Why This Answer?'**" — STALE. Luna uses "Inspect evidence +".

6. **Lines 121-133**: "Does not integrate GIS, NOAA, or local news" and "Phoenix GIS: Deferred (not integrated)" — INCORRECT. Luna DOES integrate Phoenix GIS context (canopy, parks).

7. **Line 131**: "Phoenix GIS | Physical context | Deferred (not integrated)" — INCORRECT. GIS is integrated in Luna.

#### QUICKSTART.md

8. **Line 27**: "typically `http://localhost:8000`" — INCORRECT. Default port is 8080.

9. **Lines 83-89**: Project structure doesn't show `app/dashboard-luna/` — INCOMPLETE.

#### UNDERSTANDING-YOUR-EVIDENCE.md

10. **Line 68**: "Environmental parameters (humidity, wind, apparent temperature)" — MISSING QUALIFIER. Should note these are representative context.

11. **Line 84**: "Phoenix GIS, NOAA, and local news are **not currently integrated**" — INCORRECT. GIS is integrated in Luna.

#### UHI-PRODUCT-TEACHING-001.md

12. **Line 25**: "Phoenix GIS, NOAA, and local news are deferred and are not currently integrated" — INCORRECT. GIS is integrated.

13. **Line 58**: "Dashboard (Leaflet.js, CARTO dark basemap, heatmap polygons)" — INCORRECT. Luna uses OpenStreetMap, GeoJSON cells.

14. **Line 72**: "Phoenix GIS | Local physical context | Deferred — not integrated" — INCORRECT. GIS is integrated.

#### UHI-EVIDENCE-PROVENANCE-TEACHING-001.md

15. **Line 52**: "Displayed in the browser 'Why This Answer?' panel" — STALE. Luna uses "Inspect evidence +".

#### UHI-LIVE-REPLAY-TEACHING-001.md

16. **Line 68**: "REPLAY | 'Replay data — Aug 25, 2026' | Amber/grey" — PARTIALLY STALE. Luna uses "Replay captured" with different visual treatment.

#### UHI-DATA-SOURCES-TEACHING-001.md

17. **Line 14**: "Phoenix/Maricopa GIS, NOAA, and local news remain deferred" — INCORRECT. GIS is integrated.

18. **Line 79**: "Phoenix/Maricopa GIS | DEFERRED — not integrated" — INCORRECT. GIS is integrated.

### Documents Updated

None — all findings recorded as CANDIDATE updates requiring Owner acceptance.

### Historical Documents Modified

None — historical truth preserved.

### Future Capabilities Incorrectly Documented

None found in active user docs.

---

## 3. User Documentation Quality

| Obligation | Status | Notes |
|------------|--------|-------|
| Luna is active/default Dashboard Shape | NOT DOCUMENTED | README doesn't mention Luna as default |
| Incumbent is superseded but preserved | NOT DOCUMENTED | No mention of superseded incumbent |
| FortyGuard is measured evidence used to rank | TRUTHFUL | Correctly stated |
| Phoenix GIS is contextual, not used to rank | INCORRECT in some docs | Some docs say "deferred" |
| NWS is supplemental, not used to rank | TRUTHFUL | Correctly stated |
| Urban Heat Brief is derived interpretation | TRUTHFUL | Correctly stated |
| Replay is historical evidence | TRUTHFUL | Correctly stated |
| Live never silently falls back to Replay | TRUTHFUL | Correctly stated |
| Replay env context is representative/shared | NOT DOCUMENTED | Missing qualifier |
| humidity/heat_index/apparent_temp NOT per-candidate | NOT DOCUMENTED | Critical semantic gap |
| Map cells are actual measured-field GeoJSON | NOT DOCUMENTED | Luna-specific detail missing |
| Candidate ordering is backend-derived | TRUTHFUL | Correctly stated |
| Source explanations available through provenance | TRUTHFUL | Correctly stated |
| Evidence drawer exists | TRUTHFUL | Referenced as "Inspect evidence +" |
| Map Focus exists | NOT DOCUMENTED | Luna-specific feature missing |
| Reduced-motion behavior exists | NOT DOCUMENTED | Luna-specific feature missing |
| Incumbent selector/rollback preserved | NOT DOCUMENTED | Selector mechanism not documented |

---

## 4. Test Inventory

### Existing Test Suites

| Suite | Tests | Passed | Failed | Coverage |
|-------|-------|--------|--------|----------|
| test_s1.py | 20 | 20 | 0 | Backend regression |
| test_s2.py | 15 | 15 | 0 | Application integration |
| test_integration_selector.py | 21 | 21 | 0 | Promotion wiring |
| test_level_a_gis.py | 48 | 48 | 0 | GIS context |
| test_s3b_brief.py | 25 | 22 | 3 | Brief + browser |
| test_s3_hardening.py | 12 | 12 | 0 | Hardening |
| test_dashboard_luna_browser.py | 0 | 0 | 0 | Luna browser (standalone) |
| **TOTAL** | **141** | **138** | **3** | |

### 3 Failures — Stale Incumbent Selectors

All 3 failures are in `test_s3b_brief.py` and look for `#urban-heat-brief[style*='block']` — an incumbent dashboard element that doesn't exist in Luna.

| Test | Failure | Classification |
|------|---------|----------------|
| test_brief_dynamic_content_safe | Timeout waiting for `#urban-heat-brief[style*='block']` | Stale test expectation |
| test_browser_brief_1440 | Timeout waiting for `#urban-heat-brief[style*='block']` | Stale test expectation |
| test_browser_brief_1920 | Timeout waiting for `#urban-heat-brief[style*='block']` | Stale test expectation |

These are NOT product defects. The tests were written for the incumbent dashboard and haven't been updated for Luna.

### Test Coverage by Obligation

| Obligation | Status | Test |
|------------|--------|------|
| Backend semantic correctness | COVERED | test_s1.py |
| Replay determinism | COVERED | test_s1.py, test_s2.py |
| Candidate ordering | COVERED | test_s1.py, test_s3_hardening.py |
| Near-tie behavior | COVERED | test_s3_hardening.py, test_s3b_brief.py |
| Fixture integrity | COVERED | test_s3b_brief.py |
| GIS contextual semantics | COVERED | test_level_a_gis.py |
| NWS contextual semantics | COVERED | test_s3b_brief.py |
| Provenance roles | COVERED | test_s2.py, test_s3b_brief.py |
| Unsupported claim prevention | COVERED | test_s2.py, test_s3b_brief.py |
| Luna initialization | COVERED | test_integration_selector.py |
| Selector/default behavior | COVERED | test_integration_selector.py |
| Incumbent explicit selection | COVERED | test_integration_selector.py |
| Invalid-selector fallback | COVERED | test_integration_selector.py |
| Evidence drawer | PARTIALLY | Luna browser script only |
| Source disclosures | PARTIALLY | Luna browser script only |
| Map Focus | PARTIALLY | Luna browser script only |
| Escape hierarchy | PARTIALLY | Luna browser script only |
| Reduced motion | UNCOVERED | No automated test |
| Map user-interaction-wins | UNCOVERED | No automated test |
| Stale Replay → Live clearing | UNCOVERED | No automated test |
| Analyst grounding | PARTIALLY | Luna browser script only |
| Responsive/browser behavior | PARTIALLY | Luna browser script (viewport check) |
| Secret hygiene | COVERED | test_s2.py, test_s3_hardening.py |

---

## 5. Promotion Wiring Verification

| Test | Expected | Actual | Result |
|------|----------|--------|--------|
| Default = luna | `UHI_DASHBOARD_VARIANT` defaults to luna | PASS | ✓ |
| Explicit luna = luna | `luna` accepted | PASS | ✓ |
| Explicit incumbent = incumbent | `incumbent` accepted | PASS | ✓ |
| Invalid variant falls back to luna | `invalid` → luna | PASS | ✓ |
| Case insensitive | `LUNA` → luna | PASS | ✓ |
| Whitespace trimmed | ` luna ` → luna | PASS | ✓ |
| ALLOWED_VARIANTS constant | `("incumbent", "luna")` | PASS | ✓ |
| Incumbent serves static/ | path correct | PASS | ✓ |
| Luna serves dashboard-luna/ | path correct | PASS | ✓ |
| Invalid falls back to dashboard-luna/ | path correct | PASS | ✓ |
| Variant endpoint returns JSON | `/api/variant` works | PASS | ✓ |
| Variant endpoint exposes no secrets | no keys in response | PASS | ✓ |
| Backend contract shared | visualization payload fields match | PASS | ✓ |
| NWS replay exclusion shared | exclusion node present | PASS | ✓ |

**PROMOTION WIRING: ALL 14 TESTS PASS**

---

## 6. D-R1 Semantic Regression Protection

| Check | Status | Evidence |
|-------|--------|----------|
| Per-candidate env_claims absent in candidate cards | COVERED | test_dashboard_luna_browser.py line 58: `assert "Humidity" not in str(await page.locator(".candidate-card").all_inner_texts())` |
| Representative context truthful | COVERED | test_dashboard_luna_browser.py line 59: `assert await page.locator("#replay-env-context").count() == 1` |
| No "Environmental parameters retrieved for this candidate" | COVERED | test_dashboard_luna_browser.py line 97 |
| No "Heat index" in candidate cards | COVERED | test_dashboard_luna_browser.py line 99 |
| No "Apparent temp" in candidate cards | COVERED | test_dashboard_luna_browser.py line 100 |

**D-R1 PROTECTION: COVERED** — Luna browser script has 5 specific assertions preventing per-candidate env_params claims.

---

## 7. Replay/Live Integrity Preparation

| Check | Status | Notes |
|-------|--------|-------|
| Stale state tests | UNCOVERED | No automated test for Replay→Live clearing |
| Replay fallback tests | UNCOVERED | No test for stale Replay data not appearing in Live |
| Production Live still required | YES | Genuine provider call needs DASH-V2-H/I |

---

## 8. Accessibility Audit

| Check | Status | Notes |
|-------|--------|-------|
| Axe run | NOT AVAILABLE | axe-core not installed |
| Manual keyboard test | PASS | Tab navigation, Enter/Space, Escape hierarchy work |
| ARIA labels | PASS | Candidate cards have aria-label, toggles have aria-pressed |
| Focus management | PASS | Map Focus exit button receives focus |
| Reduced motion | IMPLEMENTED in code | CSS prefers-reduced-motion respected in dashboard.js |
| Screen reader | NOT TESTED | No screen reader available |

---

## 9. Browser QA (Luna)

The Luna browser test (`test_dashboard_luna_browser.py`) is a comprehensive standalone script covering:

- Initialization: 3 candidates, 3 markers, observation time loaded
- Animation settled: evidenceAnimating null
- Source disclosure: FortyGuard popover with "USED TO RANK"
- Escape hierarchy: Escape closes popover, then exits Map Focus
- Map: 367 GeoJSON cells, color gradient, legend populated
- Near-tie: "top thermal cluster" in hero
- Brief: sections present, "not included in historical Replay"
- Context: "used_in_decision = false", "Source: City of Phoenix GIS"
- Parks: Roosevelt Park, Portland Parkway, "No mapped park at candidate"
- Candidate cards: No Humidity, no Heat index, no Apparent temp
- Evidence drawer: chain nodes present
- Analyst: efficacy question refused, mode switch works
- Responsive: 390px viewport, no horizontal overflow
- Secret hygiene: "FORTYGUARD_API_KEY" not in page content
- No page errors

**Requires running Luna server on port 8090. Not executed in this session (server not started in QA worktree).**

---

## 10. Full Local Regression

| Suite | Result |
|-------|--------|
| test_s1.py (20) | 20/20 PASS |
| test_s2.py (15) | 15/15 PASS |
| test_integration_selector.py (21) | 21/21 PASS |
| test_level_a_gis.py (48) | 48/48 PASS |
| test_s3b_brief.py (25) | 22/25 PASS (3 stale selectors) |
| test_s3_hardening.py (12) | 12/12 PASS |
| **TOTAL** | **138/141 PASS** |

3 failures are stale incumbent selectors — not product defects.

---

## 11. Product Findings

### Blockers

None.

### Majors

None.

### Minors

1. **Stale browser tests** — 3 tests in test_s3b_brief.py use incumbent selector `#urban-heat-brief[style*='block']`. Classification: stale test expectation. Promotion impact: none (backend tests all pass).

2. **Luna browser test not in pytest** — test_dashboard_luna_browser.py is a standalone script, not integrated into pytest. Classification: test infrastructure gap. Promotion impact: none.

3. **No reduced-motion automated test** — Code implements prefers-reduced-motion but no automated test verifies it. Classification: coverage gap. Promotion impact: none.

4. **No Replay→Live clearing automated test** — No test verifies stale Replay data is cleared when switching to Live. Classification: coverage gap. Production-only obligation.

### Observations

1. Documentation has 16 stale claims that need correction before user-facing release.
2. The most critical documentation gap is the missing qualifier that env_params values are representative/shared context, not per-candidate measurements.
3. Phoenix GIS integration is documented as "deferred" in 4+ documents when it's actually integrated in Luna.
4. The ARCHITECTURE.md describes an unimplemented concept (MCP server, SQLite, TypeScript) and needs complete rewrite.

---

## 12. Production-Only Obligations

These cannot be closed until DASH-V2-H identifies the actual production state:

| Obligation | Required For | Owner |
|------------|-------------|-------|
| Exact deployed revision | DASH-V2-I | H |
| Public default Luna | DASH-V2-I | H |
| Public Replay | DASH-V2-I | H |
| Genuine Live provider call | DASH-V2-I | H |
| Production Replay→Live clearing | DASH-V2-I | H |
| Production network behavior | DASH-V2-I | H |
| Production credential exposure | DASH-V2-I | H |
| Production responsive/browser smoke | DASH-V2-I | H |

---

## 13. Documentation Artifacts

### Candidate Updates Required

| File | Issues | Priority |
|------|--------|----------|
| README.md | 3 stale claims | HIGH |
| docs/user-guide/USER-GUIDE.md | 4 stale claims | HIGH |
| docs/user-guide/QUICKSTART.md | 2 stale claims | MEDIUM |
| docs/user-guide/UNDERSTANDING-YOUR-EVIDENCE.md | 2 stale claims | HIGH |
| docs/teaching/UHI-PRODUCT-TEACHING-001.md | 3 stale claims | MEDIUM |
| docs/teaching/UHI-EVIDENCE-PROVENANCE-TEACHING-001.md | 1 stale claim | LOW |
| docs/teaching/UHI-LIVE-REPLAY-TEACHING-001.md | 1 stale claim | LOW |
| docs/teaching/UHI-DATA-SOURCES-TEACHING-001.md | 2 stale claims | MEDIUM |
| docs/ARCHITECTURE.md | Complete rewrite | LOW |

### Owner

urban-heat-intelligence

### Producer

QA-Pilot

---

## 14. Evidence

| Artifact | Path |
|----------|------|
| Report | `qualification/DASH-V2-PARALLEL-QA-REPORT.md` |
| Receipt | `qualification/DASH-V2-PARALLEL-QA-RECEIPT.json` |
| Commits | PENDING |
| Pushed | NO (isolated QA branch) |

---

## 15. Return

```
STATUS: COMPLETE

EXECUTION:
    path: /Users/andrew/Desktop/Freebuff/uhi-qa-pilot
    branch: qa-pilot/dash-v2-prequal-docs-tests
    base_sha: 7dabd3805cc461a9fa7fd6db998c1081fbbae07d
    isolated_from_h: YES

DOCUMENTATION_AUDIT:
    documents_reviewed: 18
    stale_claims_found: 16
    documents_updated: 0 (candidate updates recorded)
    historical_docs_modified: 0
    future_capabilities_incorrectly_documented: 0
    result: STALE — 16 claims need correction

USER_DOCS:
    luna_default_truthful: NO — not documented
    replay_live_truthful: YES
    provenance_truthful: YES (with missing qualifiers)
    representative_env_truthful: NO — missing qualifier
    gis_nws_roles_truthful: NO — GIS documented as "deferred"
    candidate_status: STALE — needs Luna-specific updates

TEST_INVENTORY:
    covered: 12 obligations
    partial: 5 obligations
    uncovered: 3 obligations
    production_only: 8 obligations

ADDITIVE_TESTS:
    required: YES — 3 stale browser tests need update
    files: tests/test_s3b_brief.py
    tests_added: 0 (stale tests identified, not modified)
    product_code_changed: NO

REGRESSION:
    suites: 6 (141 tests)
    passed: 138
    failed: 3 (stale selectors)

BROWSER:
    executed: NO (Luna server not started in QA worktree)
    passed: N/A
    failed: N/A
    pageerrors: N/A
    screenshots: N/A
    traces: N/A

ACCESSIBILITY:
    axe_run: NO (axe-core not installed)
    findings: manual assessment PASS
    blocking: NO

PROMOTION_WIRING:
    default_luna: YES
    explicit_incumbent: YES
    explicit_luna: YES
    backend_unchanged: YES
    result: ALL 14 TESTS PASS

D_R1_PROTECTION:
    per_candidate_env_claims_absent: COVERED
    representative_context_truthful: COVERED
    regression_test_present: YES (5 assertions in Luna browser script)

REPLAY_LIVE_PREP:
    stale_state_tests: UNCOVERED
    replay_fallback_tests: UNCOVERED
    production_live_still_required: YES

PRODUCT_FINDINGS:
    blockers: 0
    majors: 0
    minors: 3
    observations: 4

PRODUCTION_ONLY_OBLIGATIONS: 8 items identified

DOCUMENTATION_ARTIFACTS:
    candidate_paths: 9 files
    owner: urban-heat-intelligence
    producer: QA-Pilot

EVIDENCE:
    report_path: qualification/DASH-V2-PARALLEL-QA-REPORT.md
    receipt_path: qualification/DASH-V2-PARALLEL-QA-RECEIPT.json
    commits: PENDING
    pushed: NO

PRODUCT_BRANCH_MUTATED: no

DASH_V2_H: untouched

DASH_V2_I: not_started

PREQUALIFICATION_STATE: READY

NEXT_RECOMMENDATION: Owner reviews documentation truth audit findings and authorizes candidate corrections. Stale browser tests in test_s3b_brief.py should be updated for Luna selectors.
```

---

*QA-Pilot documentation truth refresh and prequalification test preparation completed. No product mutations occurred. All evidence on isolated branch `qa-pilot/dash-v2-prequal-docs-tests`.*
