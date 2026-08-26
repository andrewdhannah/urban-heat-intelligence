# Urban Heat Intelligence — Hackathon Plan v3.3

**Project ID:** urban-heat-intelligence
**Version:** 3.3.0
**Supersedes:** hackathon-plan-v3.2.md (v3.2.0, 2026-08-21)
**Authorization:** Pending Owner acceptance
**Date:** 2026-08-26
**Basis:** Participant Handbook reconciliation (22 screenshots from locked PDF)

---

## Supersession Chain

```
T0 baseline (sealed 2026-08-05)
    ↓
Phase 1 discovery (2026-08-21)
    ↓
PHASE1-DECISION-PACKET-20260821
    ↓
Owner authorization (PHASE1-OWNER-AUTHORIZATION-20260821)
    ↓
v3.2 planning state (SUPERSEDED FOR EXECUTION — preserved as historical authority)
    ↓
UHI-EXTERNAL-CAPABILITY-UPDATE-20260826 (Participant Handbook evidence)
    ↓
v3.3 current execution plan (this document)
```

**Note:** T0 baseline, Phase 1 discovery, and v3.2 are preserved as immutable historical evidence. This document supersedes v3.2 for execution purposes but does not modify or delete it. See `UHI-EXTERNAL-CAPABILITY-UPDATE-20260826.json` for the transition record.

---

## What Changed from v3.2

| Dimension | v3.2 (historical) | v3.3 (current) | Source |
|-----------|-------------------|----------------|--------|
| Track | Track 01 — Resilient Cities | **Track 6 — Agentic Track** | Participant Handbook |
| Primary data source | NWS + USGS + NOAA + FortyGuard | **FortyGuard (required, central)** | Participant Handbook |
| Supplementary sources | None defined | NWS, USGS, NOAA (optional) | Handbook + Phase 1 discovery |
| API availability | Unknown / unavailable | **Available, free trial credits** | Owner obtained API key |
| Dashboard access | Unknown | **Available to execution agent** | Owner confirmed |
| Quickstart | Not referenced | **Python client + cached mode** | Participant Handbook §7 |
| Sprint model | 13 sprints (S0-S12) | **5 stages** (simplified) | Handbook scope + deadline |
| Submission requirements | 3 items (draft) | **4 items (confirmed)** | Participant Handbook §11 |
| Forecast range | 24-48h | **+12h** | Participant Handbook §7 |
| Geographic scope | U.S. + international | **U.S. only** | Participant Handbook §7 |
| Date range | Unknown | **2021-01-01 to present** | Participant Handbook §7 |
| Deployment | Optional | **P0 — live demo required** | Participant Handbook §11 |

---

## Narrative

Urban Heat Intelligence is a FortyGuard Hackathon '26 entry that turns urban heat data into actionable safety intelligence. The system wraps FortyGuard's API endpoints in an autonomous agent that plans, calls, and decides — turning a natural-language goal into a completed heat workflow with minimal human steering.

The core differentiator: **every answer shows its work.** Each response includes an evidence receipt documenting which API calls were made, what data was returned, and how the conclusion was reached.

**Track 6 — Agentic Track:** "Wrap FortyGuard's endpoints in autonomous agents that plan, call, and decide — turning a natural-language goal into a completed heat workflow with minimal human steering."

---

## Submission Requirements (Confirmed)

| # | Required | Description |
|---|----------|-------------|
| 1 | Live demo link | Working project, accessible to judges |
| 2 | Public repository | Code + README explaining how to run it |
| 3 | Demo video | ≈ 3 minutes showing the project working |
| 4 | Written summary | Max 500 words: problem → who it's for → FortyGuard endpoints used → measured result |

**Source:** Participant Handbook §11 (screenshots from locked PDF)

---

## Judging Criteria (Confirmed)

| Criterion | Weight | What Judges Look For |
|-----------|--------|---------------------|
| Impact & relevance | 40% | Real urban-heat problem with measurable benefit; commercially viable solutions a real client would adopt |
| Technical execution | 35% | It works, the build is sound, data handled well; deployable, client-grade quality |
| Innovation | 15% | Original approach or fresh combination of ideas |
| Communication | 10% | Clear, compelling demo and write-up |

**What wins:** "Real use of the platform (the API or Dashboard is central, not decorative); a clear problem and user; a measurable outcome (e.g. '-7°F (-4°C) on this route'); and a path to real-world deployment. Judges reward applied relevance over flashy demos."

**Source:** Participant Handbook page 17

---

## FortyGuard API Reality (Confirmed)

| Detail | Value |
|--------|-------|
| Base URL | `https://api.fortyguard.com` |
| Auth | `api-key: YOUR_API_KEY` header |
| Coverage | U.S. only |
| Date range | 2021-01-01 to present + 12h forecast |
| Pattern | Async: POST → get `activity_id` → poll GET `/v1/status/{activity_id}` |
| Available on all plans | `/v1/heatmap`, `/v1/env_params`, `/v1/system/fetch-api-key-usage` |
| Premium only | `/v1/satellite`, `/v1/streetview`, `/v1/heat_intelligence` |
| Quickstart | Python client + Jupyter notebooks, cached mode available |

**Source:** Participant Handbook §7 (screenshots from locked PDF)

---

## Execution Model

### Five-Stage Structure

| Stage | Name | Scope | Key Deliverables |
|-------|------|-------|-----------------|
| **Phase A** | Governed Project Instantiation | Registry, Git, identity, secrets, startup envelope | PROJECT-CREATION receipt |
| **Phase B** | Fresh-Context Re-Entry Proof | Agent resolves correct project state | Phase B qualification receipt |
| **S0** | FortyGuard Preflight + Runtime | API validation, scaffold, adapter, DB, agent skeleton, chat | Working FortyGuard integration, evidence receipts |
| **S1** | Agent + Evidence Core | Reasoning loop, evidence composition, replay mode | End-to-end agent answering heat questions with receipts |
| **S2** | Decision Experience + Replay | Dashboard, visualization, offline mode, replay | User-facing evidence inspection, demo-ready UI |
| **S3** | Deployment + Hardening | Live deployment, README, build verification | Deployed demo, public repo |
| **S4** | Submission Certification | Video, summary, final QA | Complete submission package |

### Dependency Graph

```
Phase A → Phase B → S0 → S1 → S2 → S3 → S4 → SUBMIT
```

No parallelism — sequential stages with clear gates.

### Stage Details

#### Phase A: Governed Project Instantiation

See `uhi-corrected-next-packet.md` for full specification.

- Create Librarian project entry: `urban-heat-intelligence`
- Project root: `active/hackathon26/`
- Git init with `.gitignore` excluding secrets
- `.secrets/fortyguard.env` with API key (LOCAL ONLY)
- `.env.example` with variable names only
- Startup envelope, sprint ledger, QA link
- PROJECT-CREATION receipt

#### Phase B: Fresh-Context Re-Entry Proof

- Agent starts with `start urban-heat-intelligence`
- Resolves project identity, reads docs, confirms secrets boundary
- Emits correct Mode-Entry Report

#### S0: FortyGuard Preflight + Runtime

**Scope:**
- Project scaffold (package.json, tsconfig, structure)
- FortyGuard adapter using quickstart Python client
- SQLite DB + schema + seed (Phoenix demo data)
- MCP server skeleton or agent loop
- Chat interface (HTML/TS, evidence cards)
- Agent reasoning loop (question → tools → receipt → answer)
- Offline/replay mode (cached API responses)
- FortyGuard live preflight:
  - Verify account / usage entitlement
  - Exercise official quickstart (cached mode)
  - Call `/v1/heatmap` → poll → completion
  - Call `/v1/env_params`
  - Capture raw responses as replay fixtures
  - Compare with dashboard
- S0 tests
- README

**Acceptance gate:** Working agent call to FortyGuard API returns temperature data with evidence receipt.

**Out of scope:** NWS, USGS, NOAA, derivation, visualization, deployment.

#### S1: Agent + Evidence Core

- End-to-end agent answering "What's the heat risk in Phoenix right now?"
- Evidence receipt chain (request → response → reasoning → answer)
- Multiple tool support (heatmap + env_params composition)
- Replay mode with captured genuine fixtures
- Evidence inspection UI

**Acceptance gate:** Agent answers heat questions with source-cited, receipt-backed responses.

#### S2: Decision Experience + Replay

- Dashboard with evidence cards
- "Why?" exploration (drill from answer → receipt → API call → raw data)
- Three.js thermal visualization (if time permits)
- Offline mode using replay fixtures
- Demo scenario scripting

**Acceptance gate:** Dashboard renders evidence-backed answers with drill-down.

#### S3: Deployment + Hardening

- Deploy to hosting platform (Vercel, Railway, or similar)
- Environment variables configured (FORTYGUARD_API_KEY in platform secret store)
- Public repository with README
- Build verification from clean checkout
- Error handling hardened

**Acceptance gate:** Live demo accessible at public URL.

#### S4: Submission Certification

- Demo video ≈ 3 minutes
- Written summary max 500 words
- Final QA pass
- Submission checklist verified
- Git tag for submission commit

**Acceptance gate:** All 4 submission items ready.

---

## Architecture (from v3.2, updated for v3.3)

**Stack:** TypeScript + SQLite/sqlite-vec + HTML/TS + Leaflet.js + Python (FortyGuard client)

**Three layers:**
- `/mcp` — Agent/server (tool definitions, receipts, reasoning)
- `/db` — SQLite + sqlite-vec (temperature cache, heat documents, embeddings, evidence log)
- `/interface` — Chat shell + dashboard (HTML/TS + Leaflet.js)

**Core differentiator:** Every answer shows its work via evidence receipts.

**Note on v3.2 ARCHITECTURE.md:** The file at `active/hackathon26/docs/ARCHITECTURE.md` contains v3.2 assumptions that are superseded where conflicting (international cities, 24-48h forecast, auth method uncertainty). The architecture structure (three layers, evidence receipts) remains valid. Specific parameters should be read from this v3.3 plan.

---

## Sprint Decomposition History

The original 13-sprint decomposition (S0-S12) in `hackathon-sprint-decomposition.md` is preserved as historical evidence. It is superseded for execution by the five-stage model above.

| Historical Sprint | Disposition |
|-------------------|-------------|
| S0 (Runtime & Preflight) | Absorbed into S0 + Phase A |
| S1 (Evidence Contracts) | Absorbed into S1 |
| S2 (FortyGuard Capability) | Absorbed into S0 (live preflight) |
| S3 (NWS Evidence) | Deferred — supplementary only |
| S4 (USGS/GIS) | Deferred — supplementary only |
| S5 (NOAA + Context) | Deferred — supplementary only |
| S6 (Evidence Composition) | Absorbed into S1 |
| S7 (Derivation & Intervention) | Absorbed into S1/S2 |
| S8 (Dashboard) | Absorbed into S2 |
| S9 (Cinematic Visualization) | Optional — S2 if time permits |
| S10 (Replay/Live/Provenance) | Absorbed into S0/S1 |
| S11 (Integration & Demo) | Absorbed into S3 |
| S12 (Final Certification) | Absorbed into S4 |

---

## Evidence and Provenance

### Request Evidence Format

Every FortyGuard API call produces an evidence receipt:

```json
{
  "provider": "FortyGuard",
  "authentication": "api-key",
  "credential_source": "FORTYGUARD_API_KEY",
  "credential_present": true,
  "api-key": "[REDACTED]",
  "endpoint": "/v1/heatmap",
  "request_params": { "...": "..." },
  "activity_id": "...",
  "response_status": "completed",
  "timestamp": "..."
}
```

### Secrets Invariant

Secrets may be consumed by governed execution but may not appear in canonical artifacts, receipts, logs, prompts, fixtures, screenshots, Git history, or user-visible provenance.

### Replay Evidence

- **SYNTHETIC** fixtures: TEST ONLY, marked `SYNTHETIC`, not eligible for qualification replay
- **REPLAY ELIGIBLE** fixtures: Captured from live API calls, with timestamps and request parameters
- FortyGuard quickstart cached mode provides a starting point for fixture development

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| FortyGuard API key | **AVAILABLE** | Owner obtained, in `.secrets/fortyguard.env` |
| FortyGuard dashboard | **AVAILABLE** | For visual verification |
| FortyGuard quickstart | **AVAILABLE** | Python client + cached mode |
| Node.js | Required | Runtime environment |
| SQLite | Required | Database |
| Hosting platform | Required for S3 | Vercel, Railway, or similar |
| Video recording | Required for S4 | Screen recording tool |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| FortyGuard API rate limits | Medium | High | Use cached mode, batch requests |
| Deployment platform issues | Medium | Medium | Multiple platform options |
| Time pressure (4 days) | High | High | Five-stage model is deliberately simplified |
| IP boundary uncertainty | Low | Medium | ADR-HACK-001 verification checklist |
| API response shapes differ from docs | Low | Medium | Live preflight in S0 validates early |

---

*This plan supersedes v3.2 for execution. Historical artifacts (v3.2, T0 baseline, Phase 1 discovery) are preserved as immutable evidence. The Participant Handbook (screenshots from locked PDF) is the authoritative source for competition-specific requirements.*
