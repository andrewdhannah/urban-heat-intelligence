# Urban Heat Intelligence — Execution Plan v3.4

**Version:** 3.4.0
**Date:** 2026-08-26
**Supersedes:** v3.3 (hackathon-plan-v3.3.md)
**Authority:** Owner expansion directive — vertical expansion

---

## 1. Expansion Principle

> **Expand vertically into a much better decision product, not horizontally into a long list of APIs.**

Every S3 enhancement must answer: **Will this make the three-minute demonstration meaningfully better?**

If it won't appear in the demo, improve the measured result, strengthen the FortyGuard relationship, or make the technical implementation more impressive — it doesn't belong in the remaining hackathon scope.

---

## 2. What Changed from v3.3

| Change | Detail |
|--------|--------|
| S3 decomposed | Single "Deployment + Hardening" → S3A through S3E (5 sub-stages) |
| Urban Heat Brief added | New first-class narrative output |
| Multi-source evidence added | NWS, Phoenix GIS, NOAA, Local News (optional enrichments) |
| Teaching docs added | 7 teaching documents for QA-Pilot consumption |
| User guide added | QA-Pilot produces, UHI owns |
| QA-Pilot expanded | 6 qualification areas, 8+ negative scenarios |
| Documentation expanded | Professional repo structure with distinct consumers |
| Demo rewritten | 3-minute video structure replacing 2-minute walkthrough |
| Sequencing rule added | FEATURE FREEZE → QA-Pilot (fresh context) → Owner Acceptance |

---

## 3. Track and Submission

| Property | Value |
|----------|-------|
| Competition | FortyGuard Hackathon '26 |
| Track | Track 6 — Agentic Track |
| Dates | August 18–30, 2026 |
| Primary Data Source | FortyGuard (required, central) |
| API Key | Available — confirmed |

**Submission Requirements (4):**
1. Live demo link
2. Public repository
3. ~3-minute video
4. Written summary (500 words max)

**Judging Criteria:**
- Impact: 40%
- Technical Execution: 35%
- Innovation: 15%
- Communication: 10%

---

## 4. Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| MCP Server + Data | Python stdlib, SQLite, sqlite-vec | FortyGuard client, evidence storage, caching |
| Agent + Decision Engine | Python | Planning, tool orchestration, priority scoring, evidence chain, Heat Brief |
| Interface | HTML/CSS/JS, Leaflet.js | Chat, dashboard, "Why?" panel, mode toggle |

**Sources:**
- FortyGuard: Primary (required) — heatmap, env_params
- NWS: Optional — current conditions, advisories
- Phoenix GIS: Optional — vegetation, parks, canopy
- NOAA: Optional — historical comparison, climate normals
- Local News: Optional — human-interest context only

---

## 5. Five-Stage Lifecycle

### Phase A — Governed Project Instantiation ✅ SEALED

Completed 2026-08-26. All artifacts established.

### Phase B — Fresh-Context Re-Entry Proof ✅ SEALED

Completed 2026-08-26. Fresh agent re-entered project correctly.

### S0 — FortyGuard Preflight + Runtime (PLANNED)

- FortyGuard API integration
- Async pattern (POST → activity_id → poll GET)
- REPLAY fixtures (Aug 25, 2026)
- Basic heatmap + env_params retrieval
- Evidence receipt generation
- Mode labeling (LIVE/REPLAY)

### S1 — Agent + Evidence Core (PLANNED)

- Agent planning module
- Tool orchestration (6 MCP tools)
- Evidence chain assembly
- Chat interface (LINK pattern)
- SQLite evidence log
- Basic decision response

### S2 — Decision Experience + Replay (PLANNED)

- Priority scoring (SPEC-009)
- Intervention logic (SPEC-010)
- Top-3 ranking
- "Why?" evidence panel
- Dashboard (Leaflet.js, heat overlay)
- Mode toggle (LIVE/REPLAY)

### S3A — Decision Intelligence Expansion (PLANNED — NEW)

- Top-3 expansion with multi-source evidence
- NWS integration (current conditions, advisories)
- Phoenix GIS integration (vegetation, parks, canopy)
- NOAA integration (historical comparison)
- Local news integration (human-interest context only)
- Source hierarchy enforcement
- Multi-source failure handling
- Mixed provenance display rules

**Feature freeze gate:** All S3A features must be complete and stable before S3E begins.

### S3B — Urban Heat Brief (PLANNED — NEW)

- First-class narrative brief output
- Weather-news-report format
- Source-attributed sentences
- Conditional sections (present only if source available)
- Minimum brief (FortyGuard only) capability
- Brief export (plain text, markdown)
- Brief provenance traceability

### S3C — Deployment + Hardening (PLANNED)

- Public deployment (Render)
- Error handling and graceful degradation
- Rate limiting and retry logic
- Security review (API key exposure)
- Performance optimization
- Cross-browser testing

### S3D — Documentation / Teaching Artifacts (PLANNED — NEW)

- 7 teaching documents (PRODUCT, DECISION-FLOW, LIVE-REPLAY, DATA-SOURCES, EVIDENCE-PROVENANCE, USER-JOURNEYS, FAILURE-STATES)
- Architecture documentation (ARCHITECTURE.md, DATA-FLOW.md)
- Data source documentation (DATA-SOURCES.md, PROVENANCE-MODEL.md)
- Demo scenario (DEMO-SCENARIO.md)
- README update

### S3E — Independent QA-Pilot Qualification (PLANNED — NEW)

**Runs AFTER feature freeze.** Does not run during build.

**6 Qualification Areas:**
1. Analytical correctness — rankings, calculations, timestamps, units, candidate selection
2. Provenance correctness — every displayed assertion traceable to proper provider
3. Mode correctness — Live/Replay cannot contaminate each other
4. UX/browser correctness — real browser, public deployment, multiple viewports
5. Resilience — provider unavailable, source stale, malformed response, partial availability
6. Submission reproducibility — clean checkout → configure → run → reproduce demo

**QA-Pilot also produces:**
- User guide candidate (USER-GUIDE.md, QUICKSTART.md, UNDERSTANDING-EVIDENCE.md)
- Guide verified against actual UI
- Final QA report

**Owner acceptance required** before user guide becomes canonical.

### S4 — Submission Certification (PLANNED)

- 3-minute video (new structure, see Section 7)
- ≤500-word summary
- Final repo/README check
- Submission checklist
- Final public smoke test
- Tag/release

---

## 6. Sequencing Rule

```
BUILD (S0 → S1 → S2 → S3A → S3B → S3C → S3D):
  Build features
  → Create teaching docs
  → FEATURE FREEZE
              ↓
QUALIFY (S3E):
  QA-Pilot fresh context
  → consume canonical specs/teaching docs
  → full independent qualification
  → generate user-guide candidate
  → verify guide against actual UI
  → final QA report
              ↓
ACCEPT (S3E):
  Owner acceptance of user guide + QA report
              ↓
SUBMIT (S4):
  video
  ≤500-word summary
  final repo/readme check
  submission checklist
  final public smoke
  tag/release
```

**Why this sequence:** QA-Pilot must run AFTER feature freeze, not during build. Otherwise we burn time repeatedly qualifying moving state.

---

## 7. Demo Structure (3-Minute Video)

### Opening — 20 seconds

Show Phoenix. Ask: "Where should Phoenix prioritize a cooling intervention this afternoon?"

### FortyGuard Analysis — ~40 seconds

367 thermal features appear. Agent identifies three candidate hotspots. Environmental parameters retrieved.

### Decision — ~30 seconds

Top three ranked. Priority #1 highlighted. Explain: "It isn't simply giving us the hottest pixel. It's gathering evidence about candidate locations and explaining why one deserves attention first."

### Multi-Source Intelligence — ~35 seconds

Bring in NWS (current official context), Phoenix GIS (physical/cooling context), NOAA (historical context). Show the Urban Heat Brief.

### Provenance — ~30 seconds

Click "Why?". Show evidence chain with timestamps and modes. Explain Live vs Replay.

### Governance — ~25 seconds

Briefly: "Every important result retains source, time and provenance. Replay data cannot masquerade as Live data, and an independent QA agent verifies the final product."

---

## 8. Judging Criteria Alignment

| Criterion | Weight | How We Win |
|-----------|--------|-----------|
| Impact | 40% | Urban Heat Brief makes the product usable by planners, journalists, residents |
| Technical Execution | 35% | Multi-source evidence, provenance model, graceful degradation |
| Innovation | 15% | Evidence-backed decision support (not just a dashboard) |
| Communication | 10% | 3-minute video demonstrates the full story |

---

## 9. Dependencies

| Dependency | Status | Required For |
|-----------|--------|-------------|
| FortyGuard API key | AVAILABLE | S0+ |
| NWS API | PUBLIC (no key) | S3A |
| Phoenix GIS data | OPEN DATA | S3A |
| NOAA API | PUBLIC | S3A |
| Node.js | INSTALLED | Build |
| SQLite | INSTALLED | S0+ |
| Hosting (Render) | TO CONFIGURE | S3C |
| Video recording | TO PREPARE | S4 |

---

## 10. What Does NOT Change

- Phase A and Phase B: SEALED
- FortyGuard as primary source: Central, required, always available
- Evidence receipts: Existing model extends to narrative claims
- Live/Replay separation: Becomes more important with mixed provenance
- 0 unsupported claims rule: Now applies to Heat Brief narrative
- Track 6 (Agentic Track)

---

*This plan supersedes v3.3. All S0-S4 work follows this plan.*
