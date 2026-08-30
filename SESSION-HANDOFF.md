> **⚠ HISTORICAL STATE** — This handoff reflects the project state on August 26, 2026 (Phase A). For the current post-submission state, see below.

# SESSION-HANDOFF — Urban Heat Intelligence

**Project:** urban-heat-intelligence
**Session Type:** Phase A — Governed Project Instantiation
**Date:** 2026-08-26
**Actor:** Librarian (OpenWork-Claude)
**Authority:** Phase A Authorization (UHI-PHASE-A-AUTHORIZATION-20260826)

---

## Current State

Phase A has been authorized and executed. The project is instantiated as a governed operational project.

### What Was Established

| Artifact | Status |
|----------|--------|
| Canonical project identity | `urban-heat-intelligence` registered |
| Project registry entry | `.librarian/project-index.json` updated |
| Owner binding | Andrew as canonical Owner |
| Contract ownership | urban-heat-intelligence |
| Evidence ownership | urban-heat-intelligence |
| PROJECT-IDENTITY.md | Created |
| SESSION-HANDOFF.md | This file |
| Startup contract | `startup-contract.json` materialized |
| Secrets boundary | `.secrets/`, `.env.example`, `.gitignore` established |
| Sprint namespace | Empty sprint ledger initialized |
| QA-Pilot relationship | Linked to qa-pilot project |
| Receipt/evidence locations | `qualification/receipts/` |
| Git repository | Initialized with initial provenance |
| Planning bindings | v3.3 current, v3.2 historical |

### What Was Preserved

| Artifact | Status |
|----------|--------|
| UHI-PRE-INSTANTIATION-STATE-001.json | Immutable historical |
| HACKATHON-EXTERNAL-PROJECT-QUALIFICATION-001-BASELINE.json | Sealed immutable |
| Phase 1 discovery receipts | Historical |
| Owner decisions | Historical |
| UHI-GOVERNED-LIFECYCLE-QUAL-001.md | Protected immutable |
| All qualification baseline files | Preserved |

---

## Authorization Status

| Stage | Status | Notes |
|-------|--------|-------|
| Phase A | AUTHORIZED, EXECUTED, SEALED | Governed project instantiation |
| Phase B | AUTHORIZED, EXECUTED, SEALED | Fresh-context re-entry proof |
| S0 | PLANNED | FortyGuard preflight + runtime |
| S1 | PLANNED | Agent + evidence core |
| S2 | PLANNED | Decision experience + replay |
| S3 | PLANNED | Deployment + hardening |
| S4 | PLANNED | Submission certification |

**Expansion window:** Governed by `project-state/expansion-window-20260827-29.md` (operating plan, not a lifecycle stage). Covers EXP-A0 through EXP-Q using EXP-X namespace.

**Current plan:** hackathon-plan-v3.6.1 (expansion recovery, governance corrections applied)
**Submission fallback SHA:** `c13d8eaac7b9fffda30d8db4df88659827a965f3`
**Submission target:** Saturday Aug 29, 6–7 PM
**Feature freeze:** Saturday Aug 29, ~9–10 AM

**Do not automatically continue to subsequent stages.** Each subsequent stage requires separate Owner authorization.

---

## Next Action

Expansion window authorized. Execute per `project-state/expansion-window-20260827-29.md` and hackathon-plan-v3.6.1 Section 6.2.

Key constraints:
- Feature freeze Saturday ~9–10 AM
- Nothing started after Friday afternoon becomes submission-critical
- Submission fallback: `c13d8eaac7b9fffda30d8db4df88659827a965f3`
- Target submission Saturday 6–7 PM

---

## DASH-V2-G — Luna Promotion (2026-08-28)

**Decision:** PROMOTE_LUNA
**Receipt:** `qualification/receipts/DASH-V2-G-OWNER-PROMOTION-RECEIPT.json`

| Field | Value |
|-------|-------|
| Promoted Dashboard | Luna V2 |
| Qualified SHA | `3c5b8a862c4cf3c9f2ad4c47aab0cc51f1d85fa3` |
| Backend Ancestry | `89b7216f3b1f681e2c8660eded9c1d40fbbc7982` |
| Promotion Child SHA | `a5e7039f5ffbe7d1acf34f7f8b2c304ae65b5a54` |
| Branch | `dash-v2-g-promotion-luna` |
| Mutation | `DEFAULT_VARIANT` flip only (1 line + 3 tests) |
| Incumbent | SUPERSEDED / PRESERVED (`app/static/`) |
| Active Dashboard | Luna |
| Tests | 18/18 pass |

### Incumbent Disposition

| Rule | Status |
|------|--------|
| Deleted | No |
| Preserved as historical implementation | Yes |
| Preserved as comparison control | Yes |
| Preserved as rollback/reference | Yes |
| Evidence erased | No |

### Next Gate

DASH-V2-H — production / Live integration of promoted Dashboard

---

*Session handoff established through governed Phase A instantiation. DASH-V2-G promotion materialized 2026-08-28.*

---

## Current State (Post-Submission)

**Submission completed:** August 30, 2026

| Field | Value |
|-------|-------|
| Qualified implementation | `226767c19927f1a26416cbc7a2e2b9d6d224b9db` |
| Public repo | https://github.com/andrewdhannah/urban-heat-intelligence |
| Live demo | https://urban-heat-intelligence.onrender.com/ |
| Demo video | https://youtu.be/xYDIttapi_o |
| Primary track | Track 7 — Data Analysis & Correlation |
| Secondary track | Track 1 — Resilient Cities & Infrastructure |
| Secondary track | Track 6 — Agentic AI |
| QA disposition | PASS_WITH_KNOWN_LIMITATIONS |

### Known Limitation

Genuine Live mode requires `FORTYGUARD_API_KEY` set as an environment variable on Render. Without the credential, Live queries return an explicit error (no silent fallback to Replay).

### Implementation Summary

- **Runtime:** Python stdlib `http.server`, `UHIHandler`, threaded
- **Frontend:** Luna dashboard (HTML + CSS + JS + Leaflet.js)
- **API adapters:** FortyGuard (heatmap + env_params), NWS context, Phoenix GIS
- **Orchestration:** HeatAgent with question intent routing, deterministic top-3 ranking
- **Evidence model:** 8-node evidence chain, Urban Heat Brief with claim-level provenance
- **Modes:** Replay (genuine fixtures, zero network) and Live (genuine FortyGuard API calls)
