# DASH-V2-P1 — COMPLETION RECEIPT

**AUDIENCE + MAP LEGIBILITY REFINEMENT — FINAL PRESENTATION SHAPE BEFORE DASH-V2-I**

STATUS: **COMPLETE** (bounded work done; NOT qualified — Owner review required)

---

## EXECUTION

| Field | Value |
|---|---|
| path | `/Users/andrew/Desktop/Freebuff/uhi-p1-map-legibility` |
| branch | `refinement/dash-v2-p1-map-legibility` |
| starting_sha | `7dabd3805cc461a9fa7fd6db998c1081fbbae07d` |
| qa_projection_commits_integrated | `bb09981`, `8413ae5`, `9616bd1` (cherry-picked clean, no conflicts) |
| remote_tip | `c5ac0c4de96b9ca6ba0c1963621264179c654ecc` |

## AUDIENCE

- **primary:** municipal planner, heat-response professional, other non-GIS-specialist decision-maker
- **secondary:** informed public, journalist, community stakeholder, hackathon judge
- **wording_changes:**
  - Near-tie: "The hottest measured locations are nearly tied; local context does not change the thermal ranking." (candidate cards + dynamic section explainer)
  - Local context: "Phoenix GIS describes what surrounds each candidate and does not affect the thermal ranking (used_in_decision = false)."
  - Representative replay context: "Shared historical context for the captured afternoon — not a separate measurement for each candidate."
- **unsupported_claims_added:** none (no intervention-efficacy, no per-candidate env overclaim, no GIS ranking implication)

## CANDIDATE_MARKERS

| Field | Value |
|---|---|
| old_treatment | Unstyled 30×30 divIcon with bare rank number (no CSS existed for `.candidate-marker`) |
| new_treatment | High-contrast circular target marker: dark navy `#0d3945` fill, white ring, white 17px number, amber focus ring on card sync |
| size | 42×42 CSS px (within 40–44) |
| normal_zoom_legible | Yes — verified at initial fitBounds zoom; distinct from all 5 heat-palette colors |
| card_sync | Yes — hover/focus/click toggles `.marker-focused`; marker click pans + focuses card |
| keyboard | Yes — cards focusable + Enter activates; Leaflet markers retain `tabindex=0`/`role=button` |
| mobile | Yes — 42px markers verified at 390px viewport |

## HEAT_OPACITY

| Field | Value |
|---|---|
| implemented | Yes |
| default | 65% (step-aligned, within 65–70 band) |
| range | 20–90%, step 5 |
| changes_evidence | No — 367 cells identical; canvas geometry verified identical at 25% vs 90% (58370 painted pixels both) |
| changes_ranking | No — presentation-only, no API request; candidate order verified unchanged |
| candidate_markers_affected | No — marker pane separate; computed opacity 1 verified |

## MONOCHROME

| Field | Value |
|---|---|
| implemented | Yes |
| method | CSS `grayscale(1)` filter on `.leaflet-tile-pane img` only (same OSM provider, no credentials) |
| changes_provider | No |
| changes_evidence | No — heat canvas filter `none`, markers unaffected |
| reason_if_deferred | n/a |

## SEMANTIC_INVARIANTS

| Invariant | Status |
|---|---|
| fortyguard_primary | preserved |
| replay_367 | preserved |
| candidate_order_preserved | preserved |
| representative_env_preserved | preserved |
| gis_context_only | preserved |
| gis_may_be_unavailable | preserved |
| nws_supplemental | preserved |
| replay_nws_excluded | preserved |
| brief_derived | preserved |
| live_no_replay_fallback | preserved |

## SECURITY

- **untrusted_input_non_execution:** preserved — 38 security/XSS tests pass (test_s3_hardening + test_s3b_brief)

## REGRESSION

| Field | Value |
|---|---|
| total | 160 collected (pytest) + standalone browser suite |
| passed | 159 pytest + `LUNA_BROWSER: PASS` |
| failed | 1 — `test_env_key_consumed_server_side`: requires `FORTYGUARD_API_KEY`, unavailable in this session (environment-blocked, not a product regression; passes in deployed env per H-verification) |

**Note on baseline:** packet expected "142 tests"; actual suite is 160 collected after accepted QA projections. Three latent baseline test defects (failing at `7dabd38` before any P1 change) were repaired with intent preserved: (1) heat-field color assertion now samples canvas pixels (promoted dashboard renders with `preferCanvas`, not SVG paths); (2) submit-button selector disambiguated from analyst suggestion buttons; (3) keyboard check moved to Replay state where candidate cards deterministically exist. No tests deleted, skipped, or weakened.

## BROWSER

| Field | Value |
|---|---|
| desktop | PASS (1440×900) |
| mobile | PASS (390×844, no overflow, markers visible) |
| reduced_motion | PASS (same evidence, no errors) |
| pageerrors | none |
| console_errors | none |
| horizontal_overflow | none |

## PRODUCT_SOURCE_CHANGED

yes — `app/dashboard-luna/**` only

## BACKEND_ANALYTICS_CHANGED

no — `src/`, `app/server.py`, `app/static`, `FortyGuard/` untouched

## DEPLOYED

no — Render untouched; `integration/luna-v2-reconciled` untouched (HEAD `d5938b1`)

## OWNER_REVIEW_EVIDENCE

- `evidence/p1-review/01-normal-initial-map.png`
- `evidence/p1-review/02-candidate-markers-focus.png`
- `evidence/p1-review/03-heat-low-opacity.png`
- `evidence/p1-review/04-heat-high-opacity.png`
- `evidence/p1-review/05-monochrome-basemap.png`
- `evidence/p1-review/06-mobile-view.png`

## COMMITS

| Commit | SHA |
|---|---|
| qa_projection_integration | `65b74e3`, `3142d47`, `484ef8b` (cherry-picks of `bb09981`, `8413ae5`, `9616bd1`) |
| p1_product | `c10ac26` |
| p1_evidence | `5863a8d` (tests), `c5ac0c4` (screenshots) |

## DASH_V2_I

not_started

## NEXT_RECOMMENDATION

**OWNER_REVIEW**