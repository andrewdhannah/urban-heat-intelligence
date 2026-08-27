# Urban Heat Intelligence — FortyGuard Hackathon '26

> An agentic decision-support system for urban heat intervention prioritization. Ask where Phoenix should prioritize cooling, get an evidence-backed answer from FortyGuard thermal data with visible reasoning and inspectable provenance.

**Track:** 6 — Agentic Track (API + Agentic)

## What It Does

Ask "Where should Phoenix prioritize a cooling intervention this afternoon?" and the agent:

1. Calls FortyGuard's Temperature API for live heatmap observations (2m resolution, ~367 features)
2. Ranks top-3 candidate hotspot locations by measured thermal burden
3. Calls FortyGuard Environmental Parameters for each candidate (heat index, apparent temperature, humidity)
4. Corroborates with NWS current conditions and active weather alerts
5. Returns a ranked recommendation with full 8-node evidence chain

Every answer carries provenance — data source, observation time, visualization source, and mode.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/andrewdhannah/urban-heat-intelligence.git
cd urban-heat-intelligence

# No external dependencies — Python 3.10+ stdlib only
python3 app/server.py

# Open in browser
open http://localhost:8080
```

## LIVE Mode (Optional)

To enable live FortyGuard API queries:

```bash
# Create secret store
mkdir -p .secrets
echo "FORTYGUARD_API_KEY=your-key-here" > .secrets/fortyguard.env

# Or set environment variable
export FORTYGUARD_API_KEY=your-key-here
python3 app/server.py
```

REPLAY mode (default) requires zero credentials — uses genuine FortyGuard fixtures from Aug 25, 2026.

## Deployment

### Render (recommended)

1. Push to GitHub
2. Connect repo at [render.com](https://dashboard.render.com)
3. Create a **Web Service** → Python
4. Set environment variable: `FORTYGUARD_API_KEY` (optional, for LIVE mode)
5. Deploy

### Any Python Hosting

```bash
PORT=8080 HOST=0.0.0.0 python3 app/server.py
```

The server binds to `0.0.0.0` by default (configurable via `HOST` env var).

## Architecture

| Layer | Technology |
|-------|-----------|
| Server | Python stdlib `http.server` |
| Agent | Python — planning, tool orchestration, evidence chain |
| Temperature API | FortyGuard Temperature API (heatmap + env_params) |
| Weather Context | National Weather Service API (corroboration) |
| Frontend | HTML + CSS + JavaScript + Leaflet.js |
| Map | CARTO dark basemap, FortyGuard heatmap polygons |

## Test Suites

```bash
python3 tests/test_s1.py          # S1 regression — 20 tests
python3 tests/test_s2.py          # S2 application — 15 tests
python3 tests/test_s2_browser.py  # Browser qualification — 12 tests
python3 tests/test_s2_controlled_live.py  # Controlled LIVE proof — 7 tests
```

All suites must pass before any release.

## How to Demo

1. Open the application (REPLAY auto-runs by default)
2. Observe: top-3 ranked candidate locations with comparative analysis
3. Click "Why This Answer?" to expand the 8-node evidence chain
4. Observe: NWS weather context with active alerts
5. Switch to LIVE mode (requires API key) for real-time observations
6. Observe: mode labels, observation times, visualization sources change

## Security

- No credentials in HTML, JavaScript, or browser-visible responses
- LIVE API key stored server-side only (`.secrets/` or environment variable)
- REPLAY mode requires zero network calls
- TLS certificate verification always enabled
- User input passed as URL query parameter (no body injection)

## License

Built for the FortyGuard Hackathon '26. See hackathon terms for usage rights.
