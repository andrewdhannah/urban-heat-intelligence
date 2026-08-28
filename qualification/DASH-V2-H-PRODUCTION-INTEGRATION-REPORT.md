# DASH-V2-H Production Integration Report

**Date:** 2026-08-28
**Agent:** OpenWork-Claude (DASH-V2-H execution)
**Authorization:** DASH-V2-H — PRODUCTION / LIVE INTEGRATION

## 1. Governed State

| Identity | SHA | Meaning |
|----------|-----|---------|
| Qualified Product | `3c5b8a862c4cf3c9f2ad4c47aab0cc51f1d85fa3` | Luna V2 product behavior independently verified |
| Promotion Wiring | `a5e7039f5ffbe7d1acf34f7f8b2c304ae65b5a54` | Bounded DEFAULT_VARIANT change incumbent → luna |
| Owner Receipt | `efad8e707e10bcc9ababf105b12b48c3cc595d59` | Owner PROMOTE_LUNA decision materialized |
| Handoff State | `7dabd3805cc461a9fa7fd6db998c1081fbbae07d` | Current governed project state records Luna as active |

**Branch:** `integration/luna-v2-reconciled`
**Remote Tip:** `7dabd3805cc461a9fa7fd6db998c1081fbbae07d`

## 2. Production Deployment

| Field | Value |
|-------|-------|
| Provider | Render |
| Service | urban-heat-intelligence (srv-da7puf67bikc73b0v2bg) |
| URL | https://urban-heat-intelligence.onrender.com/ |
| Source Repository | andrewdhannah/urban-heat-intelligence |
| Source Branch (pre-H) | main |
| Deployed Revision (pre-H) | fdc98b7acc60a1315c70554a8a7933ffa848d504 |
| **Source Branch (post-H)** | **integration/luna-v2-reconciled** |
| **Deployed Revision (post-H)** | **7dabd3805cc461a9fa7fd6db998c1081fbbae07d** |
| Deployment Status | succeeded / Live |
| Build | pip install -r requirements.txt |
| Start | python3 app/server.py |
| HTTPS | yes |
| Health | healthy |

**Action taken:** Changed Render deployment branch from `main` to `integration/luna-v2-reconciled` via Render dashboard. No product code modified.

## 3. Default Variant

| Check | Result |
|-------|--------|
| Expected | luna |
| Actual | luna |
| Public Variant Endpoint | /api/variant → `{"variant": "luna"}` |
| Luna Root Verified | yes — title "Luna / Urban Heat Intelligence", Luna CSS/HTML structure |
| Incumbent Preserved | yes — app/static/ retained, variant mechanism intact |

## 4. Public Replay

| Check | Result |
|-------|--------|
| Public URL Exercised | yes |
| Result | PASS |
| Heatmap Cells | 367 |
| Candidates | 3 |
| Ranking | near_tie |
| Near-tie | yes — 0.1°C tolerance, all candidates within range |
| Historical Labeling | yes — observation_time 2026-08-25T14:00:00-07:00 |
| Representative Env Truthful | yes — shared env_params across candidates |
| GIS Role | LOCAL CONTEXT, NOT USED TO RANK |
| NWS Role | SUPPLEMENTAL CONTEXT, NOT USED TO RANK (excluded from Replay) |
| Brief Role | DERIVED INTERPRETATION |
| Evidence Drawer | present |
| Provenance | FortyGuard MEASURED EVIDENCE USED TO RANK, Phoenix GIS LOCAL CONTEXT NOT USED TO RANK, NWS excluded from replay |
| Map Resolve | working |
| Map Zoom | working |
| Map Focus | working |
| Pageerrors | none |
| Console Errors | none |

## 5. Public Live

| Check | Result |
|-------|--------|
| Public URL Exercised | yes |
| Genuine Live Request | yes — mode=live, observation_time 2026-08-28T08:00:00-07:00 |
| Provider Result | FortyGuard returned live data (367 features) |
| Mode Truthful | yes — visualization_source: live |
| Replay Fallback Absent | yes — no Replay data in Live response |
| Stale Heatmap Absent | yes |
| Stale Candidates Absent | yes |
| Stale Context Absent | yes |
| Stale Brief Absent | yes |
| Current Observation Available | yes — 2026-08-28T08:00:00-07:00 |
| External Limitation | First Live request returned 502 (free instance cold start), second succeeded. Application handled gracefully. |

## 6. Mode Transition (Replay → Live)

| Check | Result |
|-------|--------|
| Replay Loaded First | yes |
| Live Requested After | yes |
| Stale State Cleared | yes — Replay heatmap/candidates cleared, Live data loaded |
| Result | PASS |

## 7. Reduced Motion

| Check | Result |
|-------|--------|
| Production Exercised | yes (browser) |
| Same Evidence | yes |
| Animation Reduced | yes |
| Errors | none |
| Result | PASS |

## 8. User Control

| Check | Result |
|-------|--------|
| Production Exercised | yes |
| User Interaction Wins | yes |
| Snapback | none observed |
| Result | PASS |

## 9. Responsive

| Check | Result |
|-------|--------|
| Desktop | PASS |
| Mobile | PASS |
| Horizontal Overflow | none |

## 10. Security

| Check | Result |
|-------|--------|
| FortyGuard Key Present Server-Side | yes (environment variable) |
| FortyGuard Key Exposed Browser | no |
| Secret in HTML | no |
| Secret in JavaScript | no |
| Secret in API Payload | no |
| Secret in Console | no |
| Result | PASS |

## 11. Network / API Health

| Check | Result |
|-------|--------|
| /api/answer | 200 (replay), 200 (live on retry) |
| /api/variant | 200 — `{"variant": "luna"}` |
| /api/config | 200 — `{"carto_basemap_key": "..."}` |
| CORS | same-origin, no issues |
| Content-Type | application/json for API, text/html for root |
| Redirects | none |
| Result | PASS |

## 12. Findings

### Blockers
None.

### Majors
None.

### Minors
1. **Cold start 502 on first Live request** — Free Render instance returned 502 on first Live API call. Second call succeeded. Application did not crash or expose errors. Classified as EXTERNAL_LIMITATION (free tier behavior).

### Observations
1. `/api/variant` previously returned 404 on old deployment (main branch at fdc98b7). Now returns correctly after deploying integration/luna-v2-reconciled.

### External Limitations
1. Free Render instance cold start delay (50s+ spinner warning shown in UI)
2. First Live API call returned 502, recovered on retry

## 13. Known Limitations (carried forward)

- Live provider unavailable during prior qualification — application handled truthfully
- axe not run
- Bounded NWS visibility observation
- Evidence drawer timestamps unavailable (minor/low impact)

## 14. Product Source Changed

No. Product code was not modified during H. Only Render deployment branch configuration was changed.

## 15. Deployment Config Changed

Yes.
- Changed Render deployment branch from `main` to `integration/luna-v2-reconciled`
- No other infrastructure changes
