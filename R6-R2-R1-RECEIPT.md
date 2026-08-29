# R6-R2-R1 RECEIPT — Browser Consumer Closure

## Failed Previous Subject
224ef1c417544d9314f2400a6b20ae46d7fba409

## New Implementation Subject
226767c19927f1a26416cbc7a2e2b9d6d224b9db

## Implementation Tree
3f1b05a472cebfa1e267434dd2ed80e5d90b8446

## Parent
224ef1c417544d9314f2400a6b20ae46d7fba409

## Branch
remediation/dash-v2-r6-r2-r1-browser-closure

## Failed Evidence
- Location: `qualification/evidence/r6r2-browser-matrix/`
- R6-R2 matrix: 43 obligations, 65 executions, 52 pass / 13 fail, 0 env-blocked

## Remediation Evidence
- Location: `qualification/evidence/r6r2-r1-browser-matrix/`
- R6-R2-R1 matrix: 43 obligations, 65 executions, 65 pass / 0 fail, 0 env-blocked

## Files Changed (implementation commit)
1. `app/dashboard-luna/css/dashboard.css` — [hidden] contract + source-cell comment update
2. `app/dashboard-luna/css/responsive.css` — mobile stacking specificity fix + compact map sizing
3. `app/dashboard-luna/js/dashboard.js` — intent routing (INTENT_ROUTES), canvas highlight overlay, NWS mode-specific orchestration
4. `tests/test_dashboard_luna_integrity_browser.py` — expanded browser assertions for all five defect groups
5. `tests/test_r6_r2_r1_intents.py` — deterministic tests for all 9 Explore catalogue questions

## Test Suite (post-remediation)
- Full suite: 239 collected, 238 passed, 1 failed (environment-blocked)
- Targeted suites: 53 passed
- Additive: 2 pytest tests (catalogue + free-form routing) + expanded browser integrity
- Failed candidate suites: 237/236/0/1 preserved baseline unchanged

## Environment Limitation
- `tests/test_live_mode.py::test_env_key_consumed_server_side`
- Reason: `FORTYGUARD_API_KEY` unavailable
- Classification: environment-blocked, not application failure
- Preserved: environment-blocked ≠ verified live behavior

## Browser Matrix
- Total obligations: 43
- Executions: 65
- Pass: 65
- Fail: 0
- Environment-blocked: 0
- All 10 previously failing obligations (15-19, 20, 26, 33, 35, 39) now PASS with before→after evidence

## Defect Groups Fixed
1. **Intent routing** (rows 15-19): ordered INTENT_ROUTES regex table replaced fragile substring matching
2. **Source-cell highlight** (rows 20, 26): canvas-rendered overlay using true tile_id, works with preferCanvas:true
3. **Mobile stacking** (row 33): responsive specificity matched to has-result specificity + compact map sizing
4. **Hidden contract** (row 35): `[hidden]{display:none !important}` defeats display:grid/flex overrides
5. **Live NWS** (row 39): mode-specific rendering branch instead of sequential-destructive calls

## Security / Provenance
- No credentials in: browser payload, static assets, logs, tests, receipt
- FortyGuard = measured evidence / ranking source
- NWS = supplemental context, used_in_decision=false, never changes ranking
- Phoenix GIS = local context, never changes ranking
- Intersection = local context, used_in_decision=false, never changes ranking
- Urban Heat Brief = derived interpretation
- Replay ≠ Live; Historical observation ≠ current forecast

## Undeclared Mutation: NONE
## Deployment: NO
## Self-Qualified: NO
## Owner Acceptance Inferred: NO
## Candidate Freeze: NO
## 3-D Started: NO
## Genuine Live Exercised: NO (deterministic mocked consumer paths only)

## Git Diff Check: PASS
## POST_FREEZE_MUTATION: NONE
