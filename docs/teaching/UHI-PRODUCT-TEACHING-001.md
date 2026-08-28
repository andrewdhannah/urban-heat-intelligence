# Urban Heat Intelligence — Product Teaching Document

**Document ID:** UHI-PRODUCT-TEACHING-001
**Purpose:** Enable a fresh agent to understand what this product is, what it does, and why it exists.
**Consumer:** QA-Pilot (independent verifier), future developers, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. What Is Urban Heat Intelligence?

Urban Heat Intelligence (UHI) is an evidence-backed heat decision-support agent built for the FortyGuard Hackathon '26 (Track 6 — Agentic Track).

It answers the question: **"Where should a city prioritize cooling intervention?"**

Unlike typical heat dashboards that show numbers, UHI explains how the answer was built — every assertion carries source attribution, timestamps, and provenance.

---

## 2. Core Product Claims

1. **Thermal intelligence from real data:** FortyGuard provides 2m-resolution thermal mapping (367+ features in a typical Phoenix query).
2. **Decision support, not just display:** The agent ranks up to three candidate locations deterministically by observed temperature; it does not use an opaque AI score.
3. **Evidence-backed:** Every displayed assertion traces to a specific data source, tool call, and timestamp.
4. **Multi-source corroboration:** FortyGuard is primary thermal evidence. Phoenix GIS provides local context (canopy, parks) that does not influence ranking. NWS is optional live-only weather context.
5. **Provenance integrity:** Live and Replay data cannot contaminate each other. Every data point carries its mode label.
6. **Human-readable output:** The Urban Heat Brief translates technical analysis into a format planners, journalists, and residents can consume.

### 2.1 Current implementation boundary

The Urban Heat Brief is a first-class dashboard output generated from the
current answer evidence. It contains Thermal Finding, Candidate
Interpretation, Weather Context, Local Context, Decision Note, and Sources sections.
Replay uses genuine FortyGuard fixtures and explicitly excludes current NWS
context. Live may include NWS context when available, marked as supplemental
and `used_in_decision: false`. Phoenix GIS provides local context (canopy,
parks) marked as `used_in_decision: false`.

---

## 3. Architecture (Three Layers)

```
Layer 1: Data Layer
├── FortyGuard API client (Python stdlib, no external deps)
├── NWS API client (Python stdlib)
└── In-memory evidence chain (Python list, not persisted)

Layer 2: Agent + Decision Engine
├── Planning module (intent classification, tool selection)
├── Tool orchestration (heatmap + env_params)
├── Top-3 candidate ranking (observed temperature, descending)
├── Near-tie semantics (0.1°C threshold)
├── Evidence chain assembly
└── Urban Heat Brief composition (claim-level provenance)

Layer 3: Interface
├── Dashboard (Leaflet.js, OpenStreetMap basemap, GeoJSON heatmap cells)
├── Inspect Evidence panel (evidence chain display)
├── Urban Heat Brief (narrative with claim provenance)
├── Source disclosures (provenance popovers)
└── Mode toggle (LIVE / REPLAY)
```

---

## 4. Data Sources and Roles

| Source | Role | Availability | Narrative Role |
|--------|------|-------------|----------------|
| FortyGuard | Primary thermal intelligence | Required — product cannot function without it | Temperature measurements, hotspot rankings |
| Phoenix GIS | Local physical context | Integrated — context only, may be unavailable | Canopy coverage, mapped parks |
| NWS | Current weather/advisory | Optional, LIVE only — enriches context | Official conditions, advisories |

**Key rule:** FortyGuard is the only required source. All others are optional enrichments. The product degrades gracefully when optional sources are unavailable.

---

## 5. Modes of Operation

### 5.1 LIVE Mode

- Makes real API calls to FortyGuard (and optional sources)
- Requires FORTYGUARD_API_KEY
- Data is current at time of query
- All responses labeled `mode: "live"`

### 5.2 REPLAY Mode

- Uses pre-recorded fixtures from genuine FortyGuard API responses
- Requires zero credentials
- Data is from Aug 25, 2026 (fixture date)
- All responses labeled `mode: "replay"`
- Default mode — works out of the box

**Architectural rule:** Live and Replay data must never contaminate each other. A mixed-provenance display must be explicitly labeled.

---

## 6. Evidence Model

Every tool response includes an evidence receipt:

Each evidence node is an in-memory dict with `step`, `data`, and `timestamp`. The "Why?" panel displays the evidence chain from the JSON API response.

**Claim taxonomy (SPEC-011):** 10 normative classes from SOURCE_OBSERVATION to UNSUPPORTED. The product must maintain 0 unsupported claims.

---

## 7. Decision Flow

```
User query
    ↓
Agent calls FortyGuard heatmap and env_params (required)
    ↓
Agent calls NWS only after successful LIVE FortyGuard data
    ↓
Agent assembles evidence chain
    ↓
Agent ranks up to three candidates by observed temperature
  and flags candidates within 0.1°C as near-tied
    ↓
Agent composes response:
  ├── Analytical view (rankings, measured conditions, evidence chain)
  └── Urban Heat Brief (narrative, human-readable)
```

GIS provides local context that does not influence thermal ranking. The product
recommends where to prioritize investigation based on observed evidence; it
does not claim intervention effectiveness or produce an opaque priority score.

---

## 8. What Makes This Different

| Typical Heat Tool | Urban Heat Intelligence |
|-------------------|------------------------|
| Shows temperature numbers | Explains what the numbers mean |
| Dashboard with charts | Conversational agent with visible reasoning |
| Single data source | Multi-source corroboration with attribution |
| No provenance | Every assertion traceable to source + timestamp |
| Static display | Interactive: click, ask, explore evidence chain |
| No failure handling | Graceful degradation with explicit disclosure |

---

## 9. Constraints and Scope

- **Hackathon scope:** FortyGuard Hackathon '26, Aug 18–30
- **Track:** Track 6 — Agentic Track
- **Primary data:** FortyGuard (required)
- **Stack:** Python 3.10+ stdlib only (no external dependencies)
- **Deployment:** Render (public URL)
- **Submission:** Live demo, public repo, ~3-min video, ≤500-word summary

---

*This document enables a fresh agent to understand the product without reading code. QA-Pilot consumes this to produce user documentation.*
