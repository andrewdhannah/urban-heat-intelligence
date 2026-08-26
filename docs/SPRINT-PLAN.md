# Two-Week Sprint Plan

## Overview

Two weeks. Solo build. Ship something that demos well.

**Priority**: Working demo > Perfect architecture. Judges see the demo, not the code.

## Scope Boundary

**Build**:
- FortyGuard heat intelligence agent
- Evidence receipts
- Source ingestion for demo-critical knowledge (OSHA/WHO thresholds)
- Minimal provenance
- Automated tests

**Do not build before submission**:
- Full QA-Pilot/Vault integration
- Full governance showcase
- LINK marketing material
- Extended documentation suite
- Hash-at-capture provenance chain

After submission, the hackathon artifact becomes the first external validation case for the larger system. The hackathon is not where you prove everything — it's where you create an artifact that can later prove everything.

---

## Week 1: Foundation (Days 1-7)

### Day 1-2: Setup + API Exploration

- [ ] Register for hackathon
- [ ] Get FortyGuard API key, read docs thoroughly
- [ ] Set up monorepo structure (`/mcp`, `/db`, `/interface`)
- [ ] Initialize TypeScript project for MCP server
- [ ] Set up SQLite database with sqlite-vec
- [ ] Make first successful API calls, understand response shapes
- [ ] Seed test data for Phoenix and one other city

**Deliverable**: Empty but wired-up monorepo, API calls working from terminal

### ⚠️ API Key Delay Contingency

If the FortyGuard API key doesn't arrive on Day 1, **do not block**. The key is the single biggest schedule risk — everything else is buildable on assumptions, but the MCP tools are not. Here's what to build first:

**Days 1-2 without API key**:
- [ ] Set up monorepo structure (`/mcp`, `/db`, `/interface`)
- [ ] Initialize TypeScript project for MCP server
- [ ] Set up SQLite database with sqlite-vec
- [ ] **Create mock API response fixtures** based on FortyGuard's published features:
  - Mock `get_temperature` response (lat/lng → temp + metadata)
  - Mock `get_heat_index` response (heat index + danger level)
  - Mock `get_forecast` response (24-hour hourly array)
  - Use realistic values for Phoenix in August (42-46°C range)
- [ ] Build MCP server against mocks (tool schemas, receipt generation)
- [ ] Build temperature_cache table and caching logic
- [ ] Start RAG ingestion pipeline (this doesn't need the API at all)

**Why this works**: The MCP server doesn't care whether the data comes from a live API or a mock fixture — the tool schema, receipt generation, and DB caching are identical. When the key arrives, you swap the mock for the real call and everything downstream already works.

**What you lose**: You can't validate that FortyGuard's actual response shapes match your assumptions. Budget 2 hours on the day the key arrives for schema validation and fixture updates.

**Deliverable**: Empty but wired-up monorepo, API calls working from terminal (or mocks if key is delayed)

### Day 3-4: MCP Server + DB Layer

- [ ] Implement `get_temperature` tool
- [ ] Implement `get_forecast` tool
- [ ] Implement `get_heat_index` tool
- [ ] Build temperature_cache table and caching logic
- [ ] Write evidence receipt schema (tool call → structured output with sources)
- [ ] Test MCP server with manual tool calls

**Deliverable**: Working MCP server that returns structured temperature data

### Day 5-6: RAG Foundation

- [ ] Collect 20-30 heat-safety reference documents
- [ ] Write ingestion pipeline: document → chunks → embeddings → sqlite-vec
- [ ] Implement `query_evidence` tool (semantic search over documents)
- [ ] Test retrieval quality — does it return relevant heat-safety info?
- [ ] Seed with WHO, EPA, and city-specific heat action plans
- [ ] **Verify accuracy**: Cross-check every safety claim in the demo's RAG scenario against source documents. OSHA thresholds and WHO guidelines must be quoted exactly — this is the one place where a misquote is worse than no quote.

> **Risk note**: The construction-worker demo scenario cites OSHA and WHO guidelines. If the RAG layer misattributes or slightly misquotes a threshold, that's synthesized advice that reads authoritative. Before demo day: verify every safety claim against the actual source documents. Show source citations prominently in the demo — not just for show, but because this is where accuracy matters beyond the hackathon.

**Deliverable**: Working RAG layer over heat-safety documents

### Day 7: Week 1 Checkpoint

- [ ] MCP server: all core tools working
- [ ] DB: caching + RAG both functional
- [ ] Evidence receipts: structured output from every tool
- [ ] Demo the agent answering "What's the heat risk in Phoenix?" from terminal
- [ ] **Quality gate**: Basic test suite passing for MCP tools, no security red flags

**Decision point**: If behind schedule, cut `get_heat_events` and `search_locations` tools — focus on the three core ones.

---

## Week 2: Interface + Polish (Days 8-14)

### Day 8-9: Chat Interface

- [ ] Build the chat shell (HTML + TypeScript)
- [ ] Wire up to MCP server (agent calls tools, shows reasoning)
- [ ] Implement card output: answer + sources + reasoning chain
- [ ] Style it clean — not fancy, but legible and intentional
- [ ] **Quality gate**: Accessibility basics (keyboard navigation, color contrast, screen reader labels)

**Deliverable**: Working chat where you ask heat questions and get evidence-backed answers

### Day 10-11: Dashboard / Map

- [ ] Add Leaflet.js map view
- [ ] Heat overlay showing temperature data geographically
- [ ] Click-to-query: click a location, agent answers about it
- [ ] Toggle between chat view and map view
- [ ] **Quality gate**: Map is keyboard-navigable, heat overlay has alt-text equivalent

**Deliverable**: Interactive map with heat data overlay

### Day 12-13: Polish + Demo Prep + Trust Package Export

- [ ] Pre-seed data for demo cities (ensure offline reliability)
- [ ] Write demo script: 3-5 questions that show the system's capabilities
- [ ] Test full flow: question → agent reasons → tools called → evidence shown → answer
- [ ] Fix any UI rough edges
- [ ] Record a 2-minute demo video (if required)
- [ ] **Export Trust Package from LINK evidence**: PRIVACY.md, SECURITY.md, ACCESSIBILITY.md, TEST-REPORT.md, API-PROVENANCE.md — these are exports from the construction record, not new documents to write (see `TRUST-PACKAGE.md`)
- [ ] **Final quality gate**: All tests pass, security review complete, accessibility validated, privacy documented, dependencies reviewed

**If LINK cannot produce these artifacts from the construction record**, that itself is useful validation information. Format what exists, note what's missing, move on.

**Deliverable**: Polished demo + Trust Package exported

### Day 14: Submit

- [ ] Final testing (full flow, offline mode, edge cases)
- [ ] Write submission description
- [ ] Submit to hackathon

---

## Quality Gates Summary

| Day | Gate | Pass Criteria |
|-----|------|---------------|
| Day 7 | Foundation | MCP tools work, basic tests pass, no security red flags |
| Day 9 | Interface | Accessibility basics (keyboard, contrast, screen reader) |
| Day 11 | Map | Map navigable, overlay labeled |
| Day 13 | Polish | All tests pass, Trust Package exported from construction record |

These gates are checkpoints, not workstreams. If the evidence exists, export it. If it doesn't, note the gap and move on. The experiment is whether these gates can be passed without adding parallel activities.

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| FortyGuard API rate limits | Cache aggressively, pre-seed demo data |
| sqlite-vec setup issues | Fall back to cosine similarity in pure SQL for small doc sets |
| Chat interface takes too long | Dashboard-only submission is still strong |
| No time for RAG | Agent without RAG still demos the core concept |
| API response format unexpected | Day 1-2 is explicitly for API exploration |
| **Scope creep (Vault/ingester/QA-Pilot)** | These are post-hackathon enhancements. Do not add to sprint scope. The hackathon creates the artifact; the larger system validates it later. |
| **Trust Package becomes manual work** | Export from LINK evidence, don't write from scratch. If LINK can't produce it, that's validation info — format what exists and move on. |

## Minimum Viable Demo

If time runs short, the absolute minimum:

1. MCP server with `get_temperature` + `get_heat_index` (2 tools)
2. Chat interface showing agent reasoning + evidence card
3. One city's data pre-seeded
4. A working demo that answers "What's the heat risk here right now?"

Everything else is bonus.
