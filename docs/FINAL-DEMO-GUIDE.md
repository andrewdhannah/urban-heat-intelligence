# Final Demo Guide — Urban Heat Intelligence

## Links

| Resource | URL |
|----------|-----|
| Live demo | https://urban-heat-intelligence.onrender.com/ |
| Demo video | https://youtu.be/xYDIttapi_o |
| Repo | https://github.com/andrewdhannah/urban-heat-intelligence |

## What to Show

### 1. Replay Auto-Loads

The dashboard opens in **Replay mode** by default. No configuration needed.

- 367 heatmap cells displayed across the Phoenix downtown AOI
- Genuine FortyGuard fixtures from August 25, 2026 (2:00 PM MST)
- Zero network calls — everything is from local fixtures
- Historical KPHX station observation included in evidence chain

### 2. Top-3 Ranked Candidates

- Three hottest locations extracted from the measured thermal field
- Deterministic ranking by observed temperature (descending)
- Near-tie detection: if candidates are within 0.1°C, the system flags them as "effectively equivalent thermal burden"
- Each candidate shows: observed temperature, heat index, apparent temperature, humidity

### 3. Source-Cell Highlighting

- Click a ranked candidate on the map
- The corresponding heatmap source cell is highlighted
- Marker overlap fan visualizes spatial clustering
- Map auto-focuses on the selected candidate

### 4. Evidence Drawer

Expand the evidence drawer to see:
- 8-node evidence chain (thermal)
- GIS context evidence chain (canopy, parks, intersections)
- Urban Heat Brief with claim-level provenance
- Each claim shows: source provider, evidence nodes, mode, observation time, `used_in_decision` flag

### 5. Switch to Live (if credential available)

- Toggle mode from Replay to Live
- Genuine FortyGuard API calls with `FORTYGUARD_API_KEY`
- NWS forecast and alerts fetched
- Phoenix GIS queries for each ranked candidate
- If no credential: explicit error message (no silent fallback to Replay)

### 6. Explore All 9 Questions

The dashboard supports these question intents:

| # | Question | Intent |
|---|----------|--------|
| 1 | "Where should Phoenix prioritize a cooling intervention this afternoon?" | Cooling prioritization |
| 2 | "What's the heat risk in downtown Phoenix right now?" | Area risk assessment |
| 3 | "Which neighborhood has the highest heat burden?" | Cooling prioritization |
| 4 | "How does temperature spread across the area?" | Temperature distribution |
| 5 | "What are the environmental conditions at the hottest location?" | Area risk assessment |
| 6 | "Which locations are effectively tied on thermal burden?" | Cooling prioritization |
| 7 | "What's the apparent temperature compared to measured?" | Area risk assessment |
| 8 | "Where should we investigate first?" | Cooling prioritization |
| 9 | "What does the thermal field look like across downtown?" | Temperature distribution |

### 7. UI Controls

- **°C/°F toggle** — Switch temperature units
- **Opacity slider** — Adjust heatmap layer opacity
- **Basemap toggle** — Switch between Carto light and dark basemaps
- **Mobile responsive** — Layout adapts to viewport width

## Key Talking Points

### FortyGuard as Central Platform

"The thermal measurement is the single source of truth. FortyGuard's 2m-resolution heatmap is what we rank on. Everything else — NWS, GIS — is contextual."

### Evidence Receipts

"Every answer carries a structured record of which tools were called, what data was returned, and why the system concluded what it concluded. Judges can verify the provenance chain."

### Replay vs Live

"Replay proves the pipeline works with genuine fixtures and zero network. Live proves it works with real FortyGuard API calls. Same code path, different data sources."

### Near-Tie Honesty

"When the top candidates are within 0.1°C, the system says so. It doesn't fabricate a ranking. That's honest decision support."

### What It Does NOT Do

- No RAG, no chat interface, no TypeScript
- No SQLite/sqlite-vec, no MCP server
- No WHO/OSHA guidance lookups
- No multi-city comparison
- No forecast-based predictions
- NWS never changes the ranking
- GIS context never changes the ranking
