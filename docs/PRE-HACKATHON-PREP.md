# Pre-Hackathon Preparation Plan

**Hackathon**: August 18–30, 2026
**Today**: August 5, 2026
**Preparation window**: 13 days (August 5–17)

The goal: On August 18th, start building — not setting up.

---

## Phase 1: API Access (Immediate — Blocking)

**Priority**: CRITICAL. Everything depends on this.

- [ ] FortyGuard API key arrives
- [ ] Read API documentation thoroughly (https://docs-api.fortyguard.com)
- [ ] Validate real API response shapes against MCP-SCHEMA.md assumptions
- [ ] Test actual endpoint: `POST /v1/heat-intelligence`
- [ ] Confirm rate limits, credit allocation, auth method
- [ ] Document any discrepancies between hackathon page example and real API

**Deliverable**: Validated API contract with real response shapes

**If key is late**: Proceed with Phase 2-5 using mock fixtures. The mock approach from SPRINT-PLAN.md already covers this.

---

## Phase 2: Environment Setup (Days 1-3)

**Priority**: HIGH. Foundation work that blocks everything.

### Monorepo Structure
```
hackathon26/
├── mcp/                    # TypeScript MCP server
│   ├── src/
│   │   ├── tools/          # MCP tool implementations
│   │   ├── receipts/       # Evidence receipt generation
│   │   └── index.ts        # MCP server entry point
│   ├── package.json
│   └── tsconfig.json
├── db/                     # SQLite + sqlite-vec
│   ├── schema.sql          # Table definitions
│   ├── migrations/
│   └── seed.ts             # Data seeding script
├── interface/              # Chat + dashboard
│   ├── index.html
│   ├── src/
│   │   ├── chat.ts         # Chat interface
│   │   ├── map.ts          # Leaflet map
│   │   └── cards.ts        # Evidence card rendering
│   └── styles/
├── docs/                   # Planning docs (already created)
├── data/                   # Seed data, mocks
│   ├── mocks/              # Mock API responses
│   ├── documents/          # Heat-safety reference docs
│   └── embeddings/         # Pre-computed embeddings
└── README.md
```

### Tooling
- [ ] Initialize TypeScript project with strict mode
- [ ] Set up ESLint + Prettier
- [ ] Configure SQLite with sqlite-vec
- [ ] Set up development server (Vite or similar)
- [ ] Configure environment variables (.env for API key)

**Deliverable**: Empty but functional monorepo

---

## Phase 3: Knowledge Base (Days 3-7)

**Priority**: HIGH. RAG quality depends on document quality.

### Document Collection (Target: 20-30 documents)

**OSHA Sources** (primary — must be osha.gov):
- [ ] OSHA Heat Illness Prevention Campaign
- [ ] OSHA Technical Manual, Section III, Chapter 4: Heat Stress
- [ ] OSHA-NIOSH Heat Safety Tool factsheet

**WHO Sources** (primary — must be who.int):
- [ ] WHO Heat and Health Guidance
- [ ] WHO Climate Change and Health factsheet
- [ ] WHO Extreme Heat Heat Action Plan guidance

**City Heat Action Plans** (municipal sources):
- [ ] City of Phoenix Heat Response Plan
- [ ] City of Miami Heat Response Plan
- [ ] City of San Jose Climate Action Plan

**Research** (peer-reviewed):
- [ ] Urban heat island effect studies
- [ ] Heat-health impact assessments

### Ingestion Pipeline
- [ ] Write document ingestion script (URL → fetch → parse → chunk → embed)
- [ ] Store in SQLite with sqlite-vec
- [ ] Test retrieval quality (10 test queries)
- [ ] Verify OSHA/WHO accuracy (cross-check thresholds)

**Deliverable**: Working RAG layer with 20-30 verified documents

---

## Phase 4: Mock Data (Days 5-7)

**Priority**: MEDIUM. Enables development without live API.

### Mock API Responses
Based on the hackathon page example:

```json
// POST /v1/heat-intelligence response
{
  "location": "Phoenix, AZ",
  "temperature_f": 112,
  "risk_level": "extreme",
  "resolution": "10mi²",
  "measured_at": "2m above ground",
  "credits_remaining": 999999
}
```

Create realistic mocks for:
- [ ] Phoenix, AZ (extreme heat — primary demo city)
- [ ] Miami, FL (humidity + heat)
- [ ] San Jose, CA (FortyGuard HQ location)
- [ ] Dubai, UAE (FortyGuard presence)
- [ ] Delhi, India (global south)

Each mock should include:
- Current temperature + heat index
- 24-hour forecast array
- Risk level classification
- Environmental parameters (humidity, wind, UV)

**Deliverable**: Mock fixtures covering 5 cities, ready for MCP server development

---

## Phase 5: Scaffolding (Days 7-12)

**Priority**: MEDIUM. Build the skeleton before the hackathon.

### MCP Server Skeleton
- [ ] Tool definitions (get_temperature, get_heat_index, get_forecast, query_evidence)
- [ ] Receipt generation schema
- [ ] DB caching logic
- [ ] Error handling (API timeout, rate limits)

### Chat Interface Skeleton
- [ ] HTML shell with message input
- [ ] Agent response area with card layout
- [ ] Evidence card component (answer + sources + receipt)
- [ ] Basic styling (clean, not fancy)

### Map Dashboard Skeleton
- [ ] Leaflet.js setup
- [ ] Phoenix map centered
- [ ] Heat overlay placeholder
- [ ] Click-to-query placeholder

**Deliverable**: Functional skeletons that can be filled in during the hackathon

---

## Phase 6: Documentation (Days 10-15)

**Priority**: LOW. Do this last, not first.

- [ ] Review hackathon rules and submission requirements
- [ ] Prepare submission description template
- [ ] Finalize demo script (DEMO-SCRIPT.md)
- [ ] Review all planning docs for completeness
- [ ] Identify any gaps in MCP-SCHEMA.md (update when API key arrives)

**Deliverable**: Submission-ready documentation

---

## Preparation Timeline

```
Aug 5-7:   API key + Environment setup (Phases 1-2)
Aug 7-10:  Knowledge base collection (Phase 3)
Aug 10-12: Mock data + Scaffolding (Phases 4-5)
Aug 12-15: Documentation + Review (Phase 6)
Aug 15-17: Buffer / API key contingency
Aug 18:    HACKATHON STARTS → Execute SPRINT-PLAN.md
```

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| API key doesn't arrive before Aug 18 | Mock fixtures ready, proceed with mocks |
| API response shapes differ from assumptions | Budget 2 hours on Day 1 for schema validation |
| RAG documents hard to find | Start with OSHA/WHO (most accessible), add city plans later |
| sqlite-vec setup issues | Fallback to cosine similarity in pure SQL |
| Too much prep, not enough buffer | Phase 6 is explicitly low priority — skip if needed |

---

## Success Criteria for August 18th

On the morning of August 18th, you should have:

- [ ] Validated API contract (or mocks ready)
- [ ] Functional monorepo with tooling
- [ ] 20-30 heat-safety documents ingested
- [ ] Mock data for 5 cities
- [ ] MCP server skeleton with tool definitions
- [ ] Chat interface skeleton
- [ ] Map dashboard skeleton
- [ ] All planning docs finalized

If you have all of these, Day 1 of the hackathon is pure building — not setup.
