# S3E Final QA Report — Urban Heat Intelligence

**Producer:** QA-Pilot (independent)
**Date:** 2026-08-27
**Status:** FINAL — awaiting Owner acceptance

---

## RESULT

**QUALIFIED_WITH_KNOWN_LIMITATIONS**

---

## CONTEXT_REENTRY

Fresh governed reasoning context. Authority manifest corrected to v3.5 (CURRENT / GOVERNING EXECUTION PLAN). All canonical paths resolve. No implementation authority inherited. Actor ≠ Role ≠ Authority. Context inheritance ≠ authority inheritance.

## IMPLEMENTATION_CANDIDATE

`c13d8eaac7b9fffda30d8db4df88659827a965f3`

## QUALIFICATION_RECORD_HEAD

`c7293f6304650f786da416696b5a6b17148120dc` (record-only follow-up: receipt hash fix, 1 file changed)

## PUBLIC_URL

`https://urban-heat-intelligence.onrender.com/`

## DEPLOYMENT_MATCH

PASS — public product functional, replays correctly, brief renders, candidates display, evidence chain works. Record-only commit c7293f6 does not mutate product code.

---

## ANALYTICAL_CORRECTNESS

| Test | Result |
|------|--------|
| 367-feature Replay source | PASS |
| Area mean (42.0321°C) | PASS |
| Candidate extraction (top-3 descending) | PASS |
| Top-3 ordering (deterministic) | PASS |
| Deltas computed correctly | PASS |
| env_params per candidate | PASS |
| Observation timestamps (fixture date) | PASS |
| Deterministic behavior (two runs identical) | PASS |
| Near-tie threshold = 0.1°C | PASS |
| Exact tie → near_tie | PASS |
| Near tie (0.0004°C spread) → near_tie | PASS |
| Clear separation → normal ranking | PASS |
| No unsupported superiority claim | PASS |

**SPEC-009/010 scope:** KNOWN_LIMITATION per SPEC-009-010-SCOPE-AMENDMENT.md. Full intervention-opportunity scoring and six-category intervention model not implemented. Deliberate strategic choice. Do not mark original obligations PASS.

---

## URBAN_HEAT_BRIEF

| Test | Result |
|------|--------|
| Brief exists | PASS |
| FortyGuard attribution | PASS |
| Near-tie narrative (equivalence language) | PASS |
| Clear-separation narrative | PASS |
| Replay weather exclusion | PASS |
| NWS used_in_decision=False | PASS |
| Brief survives NWS failure | PASS |
| FortyGuard no-data → no brief | PASS |
| Source/time distinction | PASS |
| Claim provenance (7 claims, all attributed) | PASS |
| Safe rendering (textContent) | PASS |

---

## CLAIM_TAXONOMY

SPEC-011 normative classes verified in `qualification/specifications/UHI-SPEC-011-claim-taxonomy.md`:
10 classes match exactly. PROVENANCE-MODEL.md correctly references SPEC-011 with hash `24b3ff87`.

Brief claim mapping:
- `thermal-feature-count` → SOURCE_OBSERVATION
- `thermal-leading-candidate` → SOURCE_OBSERVATION
- `thermal-apparent-temperature` → SOURCE_OBSERVATION
- `candidate-near-tie` → DERIVED_FINDING
- `candidate-near-tie-context` → DERIVED_FINDING
- `decision-note` → PRIORITY_CLASSIFICATION
- `weather-replay-exclusion` → CONTEXTUAL_STATEMENT

## UNSUPPORTED_CLAIM_COUNT

**0**

---

## LIVE_REPLAY

| Test | Result |
|------|--------|
| Replay deterministic | PASS |
| Genuine fixture (synthetic=false) | PASS |
| Zero FortyGuard network in Replay | PASS |
| Zero NWS network in Replay | PASS |
| Historical observation disclosed | PASS |
| Live genuine provider path | PASS |
| Live no Replay fallback | PASS |
| Replay cannot masquerade as Live | PASS |

---

## FIXTURE_INTEGRITY

| Test | Result |
|------|--------|
| integrity-manifest.json exists | PASS |
| Heatmap SHA-256 matches | PASS |
| Env_params SHA-256 matches | PASS |
| Corrupted fixture rejected | PASS |

---

## MULTISOURCE_PROVENANCE

| Test | Result |
|------|--------|
| FortyGuard = primary thermal authority | PASS |
| NWS = supplemental current context | PASS |
| NWS used_in_decision = false | PASS |
| GIS not integrated | PASS |
| NOAA not integrated | PASS |
| News not integrated | PASS |
| No absent source as evidence | PASS |

---

## GOVERNING_PLAN_DEVIATIONS

| Deviation | Disposition |
|-----------|-------------|
| Three-browser smoke (Chrome/Firefox/Safari) | SUPERSEDED — Chromium verified, Firefox/Safari not tested. Known limitation. |
| NWS Replay fixtures | SUPERSEDED — Owner decision validly established NWS exclusion from Replay. Resolved. |
| GIS/NOAA/news absent | KNOWN_LIMITATION — documented as deferred/optional. No conflict. |

---

## AUTHORIZATION_RECEIPT_GAP_DISPOSITION

FORMAL_AUTHORIZATION_RECEIPT_GAP preserved. No standalone authorization receipts for S0-S3. Owner authorization existed through conversation instructions. Classification: historical gap in formalization, not governance failure. Does not change qualification outcome.

---

## SECURITY_RESILIENCE

| Test | Result |
|------|--------|
| Credential never exposed | PASS |
| TLS verification (ssl.create_default_context) | PASS |
| Hostile HTML/script (zero innerHTML) | PASS |
| Invalid mode → code-level allowlist | PASS |
| Bounded public errors | PASS |
| No wildcard CORS | PASS |
| FortyGuard error bounded | PASS |
| Zero features → error | PASS |
| NWS failure → brief survives | PASS |
| Cross-mode contamination prevented | PASS |
| Corrupted fixture rejected | PASS |

---

## PUBLIC_BROWSER

| Test | Result |
|------|--------|
| Page loads | PASS |
| Replay auto-runs | PASS |
| Map renders | PASS |
| 367 polygons | PASS |
| 3 ranked candidates | PASS |
| Near-tie disclosure | PASS |
| Urban Heat Brief | PASS |
| Evidence panel | PASS |
| Mode state | PASS |
| Error behavior | PASS |
| Hostile input safe | PASS |
| Secret boundary | PASS |
| Console clean | PASS |
| Responsive 1440×900 | PASS |
| Responsive 1920×1080 | PASS |

---

## CLEAN_REPRODUCTION

| Test | Result |
|------|--------|
| Python 3.10+ | PASS (tested 3.14) |
| No external deps | PASS (stdlib only) |
| Server starts | PASS |
| Replay without credential | PASS |
| Fixtures present | PASS |

---

## PRIOR_TEST_PRESERVATION

| Suite | Count | Result |
|-------|-------|--------|
| S1 regression | 20 | 20/20 PASS (independently verified) |
| S2 application | 15 | 15/15 PASS (independently verified) |
| S3 hardening | 12 | 12/12 PASS (independently verified) |
| S3B/R1 | 25 | PASS (per receipt) |
| Browser | 12 | PASS (per receipt) |
| Controlled LIVE | 7 | PASS (per receipt) |
| **TOTAL** | **91** | **ZERO regressions** |

## TOTAL_TESTS

91

---

## TEACHING_DOC_CONSUMER_RESULT

PASS — 7 teaching documents sufficient for fresh consumer to understand product purpose, decision model, Live/Replay semantics, source hierarchy, provenance, user journeys, failure states, near-tie behavior, and Urban Heat Brief.

---

## DOCUMENTATION_GENERATION

| Artifact | Status |
|----------|--------|
| USER-GUIDE.md | Generated from teaching docs only |
| QUICKSTART.md | Generated from teaching docs only |
| UNDERSTANDING-YOUR-EVIDENCE.md | Generated from teaching docs only, corrected to normative SPEC-011 classes |

## CLOSED_LOOP_RESULT

PASS — All 17 verification checks passed. Zero discrepancies between candidate documentation and actual product behavior.

## PRODUCT_DEFECTS

0

---

## KNOWN_LIMITATIONS

1. SPEC-009 broader intervention-opportunity model not implemented (deliberate strategic choice)
2. SPEC-010 six-category intervention model not implemented (deliberate strategic choice)
3. FORMAL_AUTHORIZATION_RECEIPT_GAP: S0-S3 lack standalone authorization receipts
4. GIS/NOAA/news not integrated (documented as deferred/optional)
5. LIVE provider data availability lag (external dependency)
6. Three-browser smoke: only Chromium verified
7. Invalid mode HTTP-level test not performed (code-level verified)
8. No rate limiting implemented

---

## S3_RECOMMENDATION

**ACCEPT**

## S3_OWNER_ACCEPTANCE

PENDING

## S3_SEALED

false

## S4_STATUS

NOT AUTHORIZED

---

*This report preserves the final independent S3E qualification result. No conclusions were strengthened or weakened during materialization.*
