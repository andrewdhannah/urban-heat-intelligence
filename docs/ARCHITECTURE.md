# Architecture & Tech Stack

## Overview

Single monorepo. Three layers. One clone, one demo.

```
hackathon26/
├── mcp/            # TypeScript MCP server
├── db/             # SQLite + sqlite-vec, schemas, migrations
├── interface/      # Chat shell + dashboard (HTML/TS)
├── docs/           # This folder
└── README.md
```

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| MCP Server | TypeScript + MCP SDK | Structured tool definitions, fast to iterate |
| Database | SQLite + sqlite-vec | One file, one DB, no separate vector service |
| Embeddings | Local model or cheap API | Hackathon scale — a few dozen docs, not millions |
| Chat Interface | HTML + TypeScript | Clean rebuild of LINK pattern, no framework overhead |
| Dashboard | HTML + Leaflet or Mapbox | Interactive map, simple to demo |

## MCP Server (`/mcp`)

### Tools to Expose

1. **`get_temperature`** — Current temperature at a lat/lng coordinate
2. **`get_forecast`** — Hourly forecast for a location (next 24-48h)
3. **`get_heat_index`** — Feels-like temperature with humidity/wind factors
4. **`search_locations`** — Find areas exceeding a heat threshold
5. **`get_heat_events`** — Historical extreme heat events for a region
6. **`query_evidence`** — RAG search over heat-safety documents (sqlite-vec)

### MCP Schema Notes

- Each tool returns structured JSON with a `receipt` field containing: query parameters, timestamp, data source, confidence
- Evidence receipts are the core differentiator — every answer shows its work
- Tool descriptions should be written for an LLM to call them naturally

## Database (`/db`)

### Tables

```sql
-- Cached API responses (avoid re-fetching during demo)
temperature_cache (
  id, lat, lng, timestamp, data_json, fetched_at
)

-- Heat-safety reference documents for RAG
heat_documents (
  id, title, content, source, category, created_at
)

-- Vector embeddings for semantic search (sqlite-vec)
heat_embeddings (
  id, document_id, embedding, model_name
)

-- Evidence trail — every agent interaction logged
evidence_log (
  id, session_id, tool_name, parameters, result, reasoning, timestamp
)
```

See `DB-SCHEMA.md` for full DDL.

## Chat Interface (`/interface`)

### Rebuilt LINK Pattern

The interface follows the chat-as-presentation-layer pattern:

1. **User types a question** — "What's the heat risk in Phoenix right now?"
2. **Agent reasons visibly** — Shows which tools it's calling, what data it found
3. **Card output** — Structured response with:
   - Answer text
   - Data sources (API calls made)
   - Evidence chain (why it concluded what it concluded)
   - Confidence indicator
   - Related documents (from RAG)

### What's Different from LINK

- No Owner-authority gating (simpler — single user)
- No custody chain schema (just evidence receipts)
- Stripped down to: message input, agent response cards, simple header
- Dashboard toggle to switch between chat view and map view

## Dashboard

- Leaflet.js for interactive map
- Heat overlay showing FortyGuard temperature data
- Click a location to query the agent
- Timeline slider for forecast data
- Simple HTML, no build step needed

## API Integration

### FortyGuard Temperature API

- Free access during hackathon period
- Need to check: auth method (API key?), rate limits, response format
- Cache aggressively — demo shouldn't depend on live API calls
- Fallback: pre-seeded data from the API for offline demo

### Pre-seed Strategy

Before demo day:
1. Pull temperature data for 3-5 cities (Phoenix, Dubai, San Jose, Miami, Delhi)
2. Store in `temperature_cache`
3. Pull heat-safety reference documents (WHO heat guidelines, EPA heat index docs, city-specific heat action plans)
4. Embed and store for RAG
