# Urban Heat Intelligence — FortyGuard Hackathon '26

<p align="center">
  <img src="docs/assets/urban-heat-intelligence-hero.png"
       alt="Urban Heat Intelligence — FortyGuard Hackathon '26"
       width="100%">
</p>
<p align="center">
  <em>Concept illustration — application results and evidence are generated from the actual data pipeline.</em>
</p>

> **Turns FortyGuard heat data into ranked, explainable intervention priorities so cities know where to act first—and why.**

**Submission status:** Submitted August 30, 2026

**Tracks:**
Primary — Track 7: Data Analysis & Correlation
Secondary — Track 1: Resilient Cities & Infrastructure
Secondary — Track 6: Agentic AI

| | |
|---|---|
| **Live demo** | https://urban-heat-intelligence.onrender.com/ |
| **Demo video** | https://youtu.be/xYDIttapi_o |
| **Repository** | https://github.com/andrewdhannah/urban-heat-intelligence |

---

## What It Does

Ask "Where should Phoenix prioritize a cooling intervention this afternoon?" and the system:

1. Calls **FortyGuard's Temperature API** for heatmap observations (2m resolution, ~367 features)
2. Ranks the **top-3 candidate locations** by measured thermal burden
3. Retrieves **environmental parameters** (heat index, apparent temperature, humidity) at the priority location
4. Corroborates with **NWS conditions and alerts** (Live mode only)
5. Enriches candidates with **Phoenix GIS context** (canopy, parks, intersections) — context only, never ranking
6. Composes an **Urban Heat Brief** with claim-level provenance
7. Returns a ranked result with a full, inspectable **evidence chain**

Every answer carries provenance — data source, observation time, visualization source, and mode.

## Why It Matters

Phoenix experiences extreme urban heat. Raw temperature data doesn't answer "where do we act first?" Urban Heat Intelligence interprets thermal evidence into actionable, attributable decision support — showing not just the number, but the data source, the reasoning, and why the system is telling you what it's telling you.

## Replay / Live / Provenance

**Replay** (default) uses genuine FortyGuard API responses captured on August 25, 2026. Zero network calls. Deterministic. Fixture-verified. Historical NWS station observation and alerts are included; current NWS forecast is explicitly excluded to preserve provenance integrity.

**Live** executes genuine FortyGuard API calls with the provisioned credential. NWS provides supplemental forecast context. The two modes are never silently mixed. A failed Live request does not fall back to Replay.

**Provenance** is visible at every layer: source disclosures on each data provider, an inspectable evidence chain showing every step from question to answer, and an Urban Heat Brief with claim-level source attribution.

## Architecture

| Layer | Technology |
|-------|-----------|
| Server | Python stdlib `http.server` — zero external dependencies |
| Agent | Python — intent parsing, tool orchestration, evidence chain |
| Temperature API | FortyGuard Temperature API (heatmap + env_params) — **required, central** |
| Weather Context | National Weather Service API — supplemental, Live only, never ranking |
| Local Context | Phoenix GIS (canopy, parks, intersections) — context only, never ranking |
| Frontend | HTML + CSS + JavaScript + Leaflet.js (Luna dashboard) |
| Map | OpenStreetMap basemap + FortyGuard heatmap GeoJSON cells |

**Key invariants:**
- FortyGuard measured thermal field = ranking source (always)
- NWS = supplemental context, `used_in_decision = false`, never changes ranking
- Phoenix GIS = local context, `used_in_decision = false`, never changes ranking
- `Replay ≠ Live`; historical observation ≠ current forecast
- Failed Live does not silently fall back to Replay

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture reference.

## FortyGuard Usage

FortyGuard is the primary and required data source. The product cannot function without it.

- **Temperature API** (`POST /v1/heatmap`): 367 thermal features across Phoenix at 2m resolution — the ranking source
- **Environmental Parameters** (`POST /v1/env_params`): heat index, apparent temperature, humidity at the priority location
- **Async workflow** (POST → activity_id → poll GET): the foundation of every analysis
- **Replay fixtures**: genuine FortyGuard API responses from Aug 25, 2026, used for deterministic demonstration

## Try It

**Live demo:** https://urban-heat-intelligence.onrender.com/

Replay auto-runs on load. No credentials needed for Replay mode.

**Demo video:** https://youtu.be/xYDIttapi_o

See [docs/FINAL-DEMO-GUIDE.md](docs/FINAL-DEMO-GUIDE.md) for a guided walkthrough.

## Running Locally

```bash
git clone https://github.com/andrewdhannah/urban-heat-intelligence.git
cd urban-heat-intelligence

# No external dependencies — Python 3.10+ stdlib only
python3 app/server.py

# Open in browser
open http://localhost:8080
```

Replay mode (default) requires zero credentials and zero network calls.

To enable Live mode:

```bash
export FORTYGUARD_API_KEY=your-key-here
python3 app/server.py
```

Or create `.secrets/fortyguard.env` with `FORTYGUARD_API_KEY=your-key-here`.

## Tests / Qualification

```bash
python3 -m pytest -q
```

**Current suite:** 239 collected, 238 passed, 1 environment-blocked (missing `FORTYGUARD_API_KEY`)

**Browser matrix:** 43 obligations × 4 viewports (1920×1080, 1440×900, 768×1024, 390×844) — 65 executions, all pass

**Qualification:** PASS_WITH_KNOWN_LIMITATIONS (QA-Pilot independent qualification)

**Known limitation:** Genuine Live requires `FORTYGUARD_API_KEY` provisioned on the deployment environment.

## Security

- No credentials in HTML, CSS, JavaScript, or browser-visible network responses
- `FORTYGUARD_API_KEY` stored server-side only (environment variable or `.secrets/`)
- REPLAY mode requires zero FortyGuard and zero NWS network calls
- TLS certificate verification always enabled
- `.secrets/` is git-ignored; `.env` is git-ignored

## AI-Assisted Development

Built using an AI-assisted governed development workflow. The agent executed bounded work packages, produced evidence receipts, and stopped at defined boundaries. Human Owner decisions governed scope, authority, and acceptance.

## Documentation

| Document | Status |
|----------|--------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | **Current** — implementation architecture |
| [docs/PITCH.md](docs/PITCH.md) | **Current** — product pitch |
| [docs/FINAL-DEMO-GUIDE.md](docs/FINAL-DEMO-GUIDE.md) | **Current** — demo walkthrough |
| [docs/demo/SUBMISSION-SUMMARY.md](docs/demo/SUBMISSION-SUMMARY.md) | **Current** — submission summary |
| [docs/PROJECT-OVERVIEW.md](docs/PROJECT-OVERVIEW.md) | Historical — pre-build planning assumptions |
| [docs/DEMO-SCRIPT.md](docs/DEMO-SCRIPT.md) | Historical — pre-build hypothetical scenarios |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (old) | Superseded — replaced with current architecture |
| [docs/PITCH.md](docs/PITCH.md) (old) | Superseded — replaced with current pitch |
| [docs/MCP-SCHEMA.md](docs/MCP-SCHEMA.md) | Historical — MCP was not shipped |
| [docs/DB-SCHEMA.md](docs/DB-SCHEMA.md) | Historical — SQLite was not shipped |

## License

Built for the FortyGuard Hackathon '26. See hackathon terms for usage rights.
