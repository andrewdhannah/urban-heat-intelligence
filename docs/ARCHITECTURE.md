# Architecture & Tech Stack

## Overview

Single Python monolith serving a Luna dashboard. One process handles static files, API endpoints, and agent orchestration. No build step, no transpilation, no external database.

```
urban-heat-intelligence/
├── app/
│   ├── server.py              # UHIHandler — stdlib HTTP server + API endpoints
│   ├── dashboard-luna/        # Luna dashboard (HTML + CSS + JS + Leaflet.js)
│   │   ├── index.html
│   │   ├── css/
│   │   └── js/
│   └── static/                # Incumbent dashboard (preserved, superseded)
├── src/
│   ├── agent/
│   │   ├── adapter.py         # FortyGuardAdapter — heatmap + env_params
│   │   ├── controller.py      # HeatAgent — orchestration, ranking, evidence chain
│   │   ├── brief.py           # Urban Heat Brief composition
│   │   ├── time_resolver.py   # Observation-time lookback (Live mode)
│   │   └── run.py
│   └── tools/
│       ├── heatmap.py         # FortyGuard heatmap normalization
│       ├── env_params.py      # FortyGuard env_params normalization
│       ├── nws.py             # NWS weather context (supplemental, Live only)
│       └── gis_context.py     # Phoenix GIS (canopy, parks, intersections)
├── fixtures/
│   └── fortyguard/            # Genuine FortyGuard fixtures (Aug 25, 2026)
│       ├── heatmap/
│       ├── env_params/
│       └── integrity-manifest.json
├── docs/
└── README.md
```

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Runtime/Server | Python stdlib `http.server` + `ThreadingHTTPServer` | Zero dependencies, instant deploy |
| Frontend | HTML + CSS + JavaScript + Leaflet.js | No build step, responsive, fast |
| API Integration | `urllib.request` with verified TLS | stdlib only, no `requests` |
| Data Source | FortyGuard Temperature API | Central, required — the ranking source |
| Weather Context | NWS API | Supplemental, Live only |
| GIS Context | Phoenix open data | Context only, never ranks |
| Deployment | Render (Python web service) | Build-specific asset URLs |

## Runtime/Server (`app/server.py`)

`UHIHandler` extends `SimpleHTTPRequestHandler` and serves the active dashboard variant plus API endpoints.

### Request Routing

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/` | `serve_index` | Luna dashboard with build version injection |
| GET | `/api/answer?question=...&mode=replay` | `serve_answer` | Synchronous Replay query |
| POST | `/api/live/start` | `do_POST` | Async Live query (returns job_id) |
| GET | `/api/live/status?job_id=...` | `serve_live_status` | Poll Live job status |
| GET | `/api/nws` | `serve_nws` | Raw NWS context |
| GET | `/api/config` | `serve_config` | Non-sensitive config (Carto basemap key) |
| GET | `/api/variant` | `serve_variant` | Active dashboard variant |
| GET | `/api/version` | `serve_version` | Build identity |
| GET | `/*?v=<build>` | `serve_versioned_asset` | Immutable-cache static assets |

### Key Behaviors

- Live mode uses `POST /api/live/start` + poll pattern (bounded concurrency: 1 active job)
- Replay mode uses synchronous `GET /api/answer?mode=replay`
- Live failure does not silently fall back to Replay — explicit error states
- `FORTYGUARD_API_KEY` is server-side only, never in HTML/JS/network responses

## Frontend — Luna Dashboard (`app/dashboard-luna/`)

Responsive HTML + CSS + JS single-page application with Leaflet.js map.

### Features

- **Map focus mode** — interactive heatmap overlay with source-cell highlighting
- **Marker overlap fan** — visual spread when multiple markers cluster
- **Top-3 ranked candidates** — displayed with observed temperatures
- **Evidence drawer** — expandable provenance chain
- **Urban Heat Brief** — claim-level brief with source attribution
- **Temperature units** — °C/°F toggle
- **Opacity slider** — heatmap layer opacity control
- **Basemap toggle** — Carto light/dark
- **Mobile responsive** — layout adapts to viewport

### Question Intent Routes (parsed in `controller.py`)

| Intent Pattern | Intent | Tools Selected |
|----------------|--------|----------------|
| "prioritize", "priority", "cooling intervention", "where should" | `cooling_prioritization` | heatmap + env_params |
| "risk", "danger", "heat risk", "how hot", "feel like" | `area_risk_assessment` | heatmap + env_params |
| "distribution", "spread", "across" | `temperature_distribution` | heatmap only |
| Default | `area_risk_assessment` | heatmap + env_params |

## API Adapters

### FortyGuardAdapter (`src/agent/adapter.py`) — Central, Required

Wraps the FortyGuard Temperature API with verified TLS. Two endpoints:

1. **`/v1/heatmap`** — Returns a temperature heatmap across a polygon AOI. Each cell is a measurement at 2m resolution. The adapter submits, polls for completion, and normalizes the result.
2. **`/v1/env_params`** — Returns environmental parameters (heat index, apparent temperature, humidity) at a specific coordinate given a measured temperature.

Request flow: `submit → poll /status/{id} → normalize`. Request counts tracked for provider traffic accounting.

### NWS Context (`src/tools/nws.py`) — Supplemental, Live Only

Fetches current forecast and active alerts from the National Weather Service API.

- **Always** `used_in_decision: false`
- **Never** changes the thermal ranking
- In Replay mode: excluded entirely (historical station observation from fixtures instead)
- In Live mode: if NWS is unavailable, the `evidence_status` is set to `"unavailable"` — not a failure

### Phoenix GIS (`src/tools/gis_context.py`) — Context Only, Never Ranks

Enriches ranked candidates with local context from Phoenix open data:

- **Tree canopy** — percentage from Maricopa Association of Governments
- **Parks** — whether the coordinate falls inside a designated park
- **Intersections** — nearest named intersection and distance

GIS context is additive and compositional — it MUST NOT alter the thermal ranking. GIS failure MUST NOT invalidate the thermal result.

## Orchestration — HeatAgent (`src/agent/controller.py`)

### Evidence Chain (8 nodes, thermal)

```
user_request → plan → heatmap_request → heatmap_result
→ coordinate_selection → env_params_request → env_params_result → answer
```

Plus optional GIS context evidence chain:
```
canopy_request → canopy_result → parks_request → parks_result
→ context_enrichment_result
```

### Candidate Derivation

1. FortyGuard heatmap returns `N` cells (typically 367 for the demo AOI)
2. Cells are sorted by measured temperature (descending)
3. Top-3 candidates extracted as intervention-priority locations
4. Each candidate gets `env_params` for heat index / apparent temperature

### Ranking Rules

- **Source of truth:** FortyGuard measured thermal field only
- **Ranking basis:** Observed temperature at 2m resolution
- **Near-tie threshold:** Within 0.1°C (`TIE_THRESHOLD_CELSIUS`)
- **When near-tie:** Candidates are reported as "effectively equivalent thermal burden" — additional context needed to distinguish
- **GIS never ranks:** Context enrichment is informational only

## Evidence Model

### Evidence Chain Nodes

Every query produces a structured evidence chain. Each node records:
- `step` — what operation was performed
- `data` — operation-specific data (endpoints, coordinates, results, modes)
- `timestamp` — UTC ISO-8601

### Urban Heat Brief (`src/agent/brief.py`)

A derived interpretation composed from the evidence chain. Contains:

- **Sections:** Thermal Finding, Candidate Interpretation, Weather Context, Local Context, Decision Note
- **Claims:** Each claim has `claim_id`, `text`, `source_provider`, `evidence_nodes`, `mode`, `observation_time`, `used_in_decision`
- **Sources:** Provider-level provenance (FortyGuard, NWS, Phoenix GIS)
- **Ranking status:** `ranked` or `near_tie`

The Brief does not call providers — it composes from already-normalized evidence.

## Modes

### Replay Path

- Uses genuine FortyGuard fixtures from August 25, 2026 (2:00 PM MST)
- **Zero network calls** — all data from `fixtures/fortyguard/`
- Fixture integrity validated against SHA-256 manifest
- Historical KPHX station observation included from `fixtures/nws-historical/`
- NWS current context excluded (historical snapshot only)

### Live Path

- Genuine FortyGuard API calls with `FORTYGUARD_API_KEY`
- Bounded lookback to find latest available observation
- NWS forecast and alerts fetched in parallel
- Phoenix GIS queries for each ranked candidate
- If FortyGuard fails → explicit error (no fallback to Replay)

### Mode Isolation

Each mode's data is self-contained. No cross-mode fallback is permitted:
- Replay geometry is never substituted for Live data
- Live data is never substituted for Replay data
- Visualization fields are explicitly null when a mode's data is unavailable

## Secret Boundary

| Secret | Location | In HTML/JS? | In Network Responses? |
|--------|----------|-------------|----------------------|
| `FORTYGUARD_API_KEY` | Server-side env / `.secrets/` | Never | Never |
| `CARTO_BASEMAP_KEY` | Server-side env (non-sensitive) | Via `/api/config` | Yes (public basemap key) |

## Deployment

- **Platform:** Render (Python web service)
- **Build identity:** `RENDER_GIT_COMMIT` or `GIT_COMMIT` env var
- **Asset versioning:** `?v=<build>` query parameter with immutable cache headers
- **Dashboard variant:** `UHI_DASHBOARD_VARIANT` env (default: `luna`)
- **Port:** `PORT` env (default: 8080)

## Failure Semantics

| Failure | Behavior |
|---------|----------|
| Live FortyGuard API failure | Explicit error state — does NOT fall back to Replay |
| Live NWS unavailable | `evidence_status: "unavailable"` — not a failure |
| GIS context failure | Graceful degradation — thermal result unaffected |
| Replay fixture missing | Error answer — "Heatmap call failed" |
| Live capacity exhausted | HTTP 429 with error message |
