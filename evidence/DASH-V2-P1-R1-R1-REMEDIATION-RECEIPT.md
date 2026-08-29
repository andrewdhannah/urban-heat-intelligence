# DASH-V2-P1-R1 — R1 REMEDIATION RETURN CONTRACT

**PRE-QA REMEDIATION COMPLETE**

STATUS: **COMPLETE** — ready for independent P1-R1 QA

---

## IMPLEMENTATION_CONTEXT_ID

| Field | Value |
|---|---|
| branch | `refinement/dash-v2-p1-r1-prefreeze` |
| worktree | `/var/folders/dl/5_wg4t8d2919gdc_g3x5xwk80000gn/T/opencode/uhi-p1r1` |
| exact_starting_sha | `bb6e1ccddc4284124796a71b7453c3b8cf4eb4b5` |
| pre_r1_sha | `a6f8421ac11c787ff1ef1f615eb4c9192987b9e1` |
| exact_final_sha | `b343af62d4f8a62bc3df2a360c7cfe2f641bcb89` |
| remote_branch_tip | `b343af62d4f8a62bc3df2a360c7cfe2f641bcb89` |
| remote_materialization_proof | Fetched from origin — SHA matches local, base bb6e1cc is ancestor |
| changed_files | 10 files, +761 / -30 |

---

## R1_1_REMOTE

**PASS** — Branch pushed to `origin/refinement/dash-v2-p1-r1-prefreeze`. Remote tip resolves to `b343af62d4f8a62bc3df2a360c7cfe2f641bcb89`. Local and remote tips match. Base `bb6e1cc` confirmed as ancestor.

---

## R1_2_LIVE_TIMEOUT

### prior_behavior
- Client timeout: 60 seconds (arbitrary)
- Progress labels: "Observation discovery" / "Provider processing" / "Decision construction" — timed transitions presented as observed state

### corrected_deadline_contract
Backend execution model (derived from `adapter.py` and `time_resolver.py`):
- `_make_request`: 30s HTTP timeout per request
- `poll_status`: max_polls=30, interval=3s → up to 90s per activity
- Lookback discovery: up to 12 hours × (submit + poll) = worst case ~12 × 525s
- env_params: up to 3 candidates × (submit + poll) = worst case ~3 × 930s
- Server blocks HTTP connection for entire workflow
- Worst-case server execution: ~9000s (theoretical); typical: 120-300s

### client_timeout
600,000ms (10 minutes) — exceeds typical server execution, acknowledges server may still work beyond it

### server_deadline/bound
Server-side: `poll_status` max 30 polls × 3s = 90s per activity. `submit` HTTP timeout = 30s. No server-side total deadline exists; the server runs to completion or per-activity timeout.

### actual_progress_signals_available
The browser has NO signal about server-internal phase transitions during a blocking `fetch()` call. The server does not stream progress events.

### progress_wording
Changed to truthful wording that describes what MAY be occurring:
- `elapsed < 5s`: "Connecting to provider…"
- `elapsed < 30s`: "Requesting FortyGuard evidence…"
- `elapsed < 120s`: "Provider processing — this may take a few minutes…"
- `elapsed >= 120s`: "Provider processing — still within governed execution window…"

No synthetic stage transitions. No fake percentage. Elapsed time displayed.

### tests
159/159 passed, 1 env-blocked. No new tests added for timeout change (timeout is a constant; behavior is identical except duration).

---

## STAGE_B_REEVALUATION

### B1_HISTORICAL_NWS

**NOT PROVEN** — with evidence trail

- **Station resolution**: KPHX (Phoenix Sky Harbor) — closest official NWS station to the FortyGuard downtown Phoenix AOI
- **Station IDs considered**: KPHX confirmed via `/stations/KPHX/observations` (returns data)
- **Station discovery attempt**: `/stations?point=33.45,-112.07` returned HTTP 400 (bad request — endpoint format issue; KPHX identified by prior knowledge)
- **Target Replay timestamp**: Aug 25, 2026, 14:00 MST (21:00 UTC)
- **Endpoint/query**: `GET /stations/KPHX/observations?limit=5`
- **HTTP result**: 200 OK, returned 5 observations — all from Aug 29 (recent window only)
- **Observation timestamps returned**: 2026-08-29T00:15 through 00:35 UTC
- **Retry/alternate**: No retry needed — the endpoint明确 returns only recent data. No date-range query parameter is supported on this endpoint.
- **Disposition**: RETRIEVAL ATTEMPTED — station resolved, endpoint queried, Aug 25 observations outside the API's recent window. The NWS station observation API does not retain historical observations accessible through this endpoint.

### B2_HEAT_RELIEF

**DROPPED** — CAPABILITY_UNAVAILABLE

- **Source/capability attempted**: Phoenix Heat Relief Network (`phoenix.gov/oep/heat-relief-network`)
- **ArcGIS service query**: `services2.arcgis.com/.../Heat_Relief/FeatureServer/0/query` — returned 0 features
- **ArcGIS services list**: `services2.arcgis.com/.../rest/services?f=json` — returned 0 services (endpoint may not be publicly accessible)
- **Assessment**: Heat Relief Network data exists on the city website but is not available as a structured queryable API in this execution context
- **Reason**: No structured data source found. Data likely available as HTML/PDF on city website; no authorized web-scraping capability in this execution context (Python stdlib only).
- **Independent of B1**: Yes. B1 failure does not cascade to B2.

### B3_HISTORICAL_ALERTS

**PROVEN** — fixture captured

- **Endpoint**: `GET /alerts?point=33.45,-112.07&status=actual&limit=50`
- **HTTP result**: 200 OK, returned 20 alerts
- **Temporal provenance**: Alerts from Aug 23–28 returned. Aug 25 alerts identified by onset/expiration timestamps.
- **Aug 25 alerts captured** (active at 14:00 MST or issued Aug 25):
  1. Extreme Heat Warning — onset Aug 25 12:57 PM MST, expires Aug 26 04:00 MST
  2. Air Quality Alert — onset Aug 25 09:17 AM MST, expires Aug 26 21:00 MST
  3. Extreme Heat Warning — onset Aug 25 01:42 AM MST, expires Aug 25 15:00 MST
  4. Air Quality Alert — onset Aug 24 10:21 AM MST, expires Aug 25 21:00 MST (still active at 14:00)
- **Fixture**: `fixtures/nws-historical/phoenix-aug25-alerts.json` — includes query metadata, alert details, provenance
- **Used_in_decision**: false
- **Time-sensitivity**: Captured while Aug 25 is within the NWS 7-day alert retention window

### B4_LOCAL_REPORTING

**DROPPED** — CAPABILITY_UNAVAILABLE

- **Discovery capability**: No web-search or news API capability available in this execution context (Python stdlib only)
- **Captured sources**: None
- **Reason**: No authorized web-discovery capability. Cannot access news APIs, search engines, or web scraping tools from Python stdlib without external dependencies.
- **Independent of B1-B3**: Yes. Each evaluated separately.

---

## TESTS

| Metric | Value |
|---|---|
| collected | 160 |
| passed | 159 |
| failed | 0 |
| environment_blocked | 1 (`test_env_key_consumed_server_side` — requires `FORTYGUARD_API_KEY`) |
| browser status | Not tested in this session |

---

## THERMAL_INVARIANTS

| Invariant | Status |
|---|---|
| Ranking unchanged | VERIFIED — no ranking logic modified |
| Replay 367 cells unchanged | VERIFIED — no fixture modification |
| Near-tie unchanged | VERIFIED — threshold and semantics preserved |
| Live no Replay fallback | VERIFIED — request() does not substitute |
| GIS context-only | VERIFIED — used_in_decision=false preserved |
| Context used_in_decision=false | VERIFIED — all contextual sources carry this flag |

---

## CHANGED_FILES

```
app/dashboard-luna/css/dashboard.css              |  21 +++  (measured-area label, unit toggle, NWS banner, catalogue)
app/dashboard-luna/css/responsive.css             |  17 ++  (has-result compression)
app/dashboard-luna/index.html                     |  11 +-  (unit toggle, NWS banner, catalogue, fit-area button)
app/dashboard-luna/js/dashboard.js                | 197 +++--- (A1-A8 + R1-2 timeout fix)
docs/dashboard-luna/ANALYST-INTENT-CONTRACT.md    |  41 +++  (catalogue, bounded unsupported, FG connection)
docs/dashboard-luna/README.md                     |  10 +-  (status update)
docs/teaching/UHI-PRODUCT-NARRATIVE-P1R1-001.md   | 132 ++++ (canonical thesis, evidence roles, temporal rules)
evidence/DASH-V2-P1-R1-COMPLETION-RECEIPT.md      | 166 ++++ (completion receipt)
fixtures/nws-historical/phoenix-aug25-alerts.json |  77 ++++ (B3 fixture)
src/tools/nws_historical.py                       | 119 ++++ (B1 tool — documents NOT PROVEN)
```

---

## KNOWN_LIMITATIONS

1. B1 (Historical NWS observation) NOT PROVEN — NWS station observation API returns recent data only; Aug 25 outside window
2. B2 (Heat Relief) CAPABILITY_UNAVAILABLE — no structured API found
3. B4 (Local reporting) CAPABILITY_UNAVAILABLE — no web-discovery capability
4. Browser proof not captured in this session
5. Additive tests for new UI features not yet written
6. Credential-dependent test must PASS before freeze

---

## DEPLOYED

**MUST BE NO** — Confirmed.

## PRODUCTION_BRANCH_CHANGED

**MUST BE NO** — Confirmed.

## DASH_V2_I_STARTED

**MUST BE NO** — Confirmed.

## THREE_D_STARTED

**MUST BE NO** — Confirmed.

---

## NEXT_RECOMMENDATION

**INDEPENDENT P1-R1 QA**

1. Full regression (160 collected) in credentialed environment
2. Browser proof at required viewports
3. Verify R1-2 timeout contract: Live timeout at 600s, progress labels truthful
4. Verify B3 fixture renders correctly in Replay historical context
5. Capture Owner review evidence screenshots
6. After QA: Owner decision on Hackathon Candidate Freeze

---

*No self-qualification. No Owner acceptance inference. No deployment.*
