# MCP Tool Schema — FortyGuard Temperature API

## Overview

This document defines the MCP tools that wrap FortyGuard's Temperature API. Each tool returns structured data plus an evidence receipt.

> **Note**: Final tool schemas depend on FortyGuard's actual API response shapes. This is a working draft based on the hackathon brief and typical weather/temperature API patterns. Validate against FortyGuard's API docs during Day 1-2.

---

## FortyGuard API — What We Now Know

### Core Tech
- **tOS** (Temperature Operating System): FortyGuard's AI-powered infrastructure for managing, transforming, analyzing, and optimizing urban temperature data
- **Large Temperature Models (LTMs)**: NVIDIA-recognized foundational AI models for predicting temperature patterns across urban areas
- **tcMap System** (Temperature Classification Mapping): Proprietary tool delivering high-resolution granular temperature data as NxN meter-squared tiles
- **Resolution**: 2-meter precision (115x more accurate than conventional weather models)
- **Data volume**: 52 billion data points daily

### API Features (from pricing page)
| Feature | Basic ($79/mo) | Pro ($289/mo) | Hackathon (Free) |
|---------|---------------|--------------|-----------------|
| API Credits | 1M/month | 5M/month | TBD (likely generous) |
| Heatmap Generation | Up to 10 mi² | Up to 50 mi² | TBD |
| Environmental Parameters | Up to 3 (user-selected) | Full Access | TBD |
| Satellite Segmentation | — | ✓ | TBD |
| Street View Segmentation | — | ✓ | TBD |
| Heat Intelligence | — | 2 out of 5 | TBD |

### API Documentation
- **URL**: https://docs-api.fortyguard.com/docs/introduction (JS-rendered, need to check with API key)
- **Dashboard**: https://dashboard.fortyguard.com
- **Auth**: API key (likely in header or query param — confirm with docs)

### Key API Capabilities for Hackathon
- **Temperature data**: Current, historical, forecasted — at 2m resolution
- **Heatmap generation**: Create heat overlays for specific areas
- **Environmental parameters**: Temperature + up to 3 additional factors (humidity, wind, etc.)
- **Heat intelligence reports**: Derived insights, not just raw data
- **Geographic coverage**: Global (Phoenix, Dubai, San Jose, etc.)

### API Pattern (From Hackathon Page)

The hackathon page shows a **synchronous** POST endpoint:

```
POST /v1/heat-intelligence
{
  "location": "Phoenix, AZ",
  "temperature_f": 112,
  "risk_level": "extreme",
  "resolution": "10mi²",
  "measured_at": "2m above ground",
  "credits_remaining": 999999
}
```

**Key observations**:
- Endpoint: `POST /v1/heat-intelligence`
- Synchronous response (not async as GPT suggested — the page example shows a direct response)
- Returns: location, temperature_f, risk_level, resolution, measured_at, credits_remaining
- Resolution shown as "10mi²" (heatmap coverage), but measured_at confirms "2m above ground" measurement
- Credits: 999999 remaining (generous for hackathon)

**Note**: This may be a simplified marketing example. The actual API docs (behind auth) may show a more complex interface. Validate against real API responses when key arrives.

The receipt architecture still works — anchor to the API response as the lifecycle event:

```json
{
  "source": "FortyGuard Temperature API",
  "endpoint": "POST /v1/heat-intelligence",
  "location": "Phoenix, AZ",
  "temperature_f": 112,
  "risk_level": "extreme",
  "resolution": "10mi²",
  "measured_at": "2m above ground",
  "retrievedAt": "...",
  "temperatureDataHash": "..."
}
```

### API Credits Strategy
- Hackathon likely provides free credits — confirm allocation
- Cache aggressively to conserve credits during demo
- Pre-seed data for demo cities to avoid live API dependency

---

## Tool Definitions

### `get_temperature`

**Purpose**: Get current temperature at a specific location.

```json
{
  "name": "get_temperature",
  "description": "Get the current temperature at a 2-meter resolution for a specific lat/lng coordinate. Returns temperature in Celsius and Fahrenheit, feels-like temperature, and measurement metadata.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lat": { "type": "number", "description": "Latitude coordinate" },
      "lng": { "type": "number", "description": "Longitude coordinate" },
      "units": { "type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius" }
    },
    "required": ["lat", "lng"]
  }
}
```

**Response shape** (draft):
```json
{
  "temperature": 42.3,
  "units": "celsius",
  "feels_like": 45.1,
  "location": { "lat": 33.4484, "lng": -112.0740 },
  "resolution": "2m",
  "timestamp": "2026-08-05T14:00:00Z",
  "receipt": {
    "tool": "get_temperature",
    "source": "fortyguard_api",
    "query_time": "2026-08-05T14:01:23Z",
    "cached": false
  }
}
```

---

### `get_forecast`

**Purpose**: Get hourly temperature forecast for a location.

```json
{
  "name": "get_forecast",
  "description": "Get hourly temperature forecast for a specific location. Returns up to 48 hours of forecast data at 2-meter resolution.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lat": { "type": "number", "description": "Latitude coordinate" },
      "lng": { "type": "number", "description": "Longitude coordinate" },
      "hours": { "type": "integer", "description": "Number of forecast hours (max 48)", "default": 24 }
    },
    "required": ["lat", "lng"]
  }
}
```

**Response shape** (draft):
```json
{
  "location": { "lat": 33.4484, "lng": -112.0740 },
  "forecast": [
    { "hour": "2026-08-05T15:00:00Z", "temp": 42.8, "feels_like": 45.6 },
    { "hour": "2026-08-05T16:00:00Z", "temp": 43.1, "feels_like": 46.0 }
  ],
  "receipt": {
    "tool": "get_forecast",
    "source": "fortyguard_api",
    "query_time": "2026-08-05T14:01:23Z",
    "cached": false
  }
}
```

---

### `get_heat_index`

**Purpose**: Calculate heat index with humidity and wind factors.

```json
{
  "name": "get_heat_index",
  "description": "Calculate the heat index (feels-like temperature) accounting for humidity, wind speed, and solar radiation. Returns danger level classification.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lat": { "type": "number", "description": "Latitude coordinate" },
      "lng": { "type": "number", "description": "Longitude coordinate" },
      "include_breakdown": { "type": "boolean", "description": "Include factor breakdown in response", "default": false }
    },
    "required": ["lat", "lng"]
  }
}
```

**Response shape** (draft):
```json
{
  "heat_index": 48.2,
  "danger_level": "extreme",
  "danger_color": "#FF0000",
  "factors": {
    "temperature": 42.3,
    "humidity_pct": 35,
    "wind_speed_kmh": 8,
    "solar_radiation": "high"
  },
  "recommendations": [
    "Avoid outdoor activity during peak hours",
    "Drink water every 15-20 minutes",
    "Seek air-conditioned spaces"
  ],
  "receipt": {
    "tool": "get_heat_index",
    "source": "fortyguard_api + local_calculation",
    "query_time": "2026-08-05T14:01:23Z"
  }
}
```

---

### `search_locations`

**Purpose**: Find areas exceeding a heat threshold.

```json
{
  "name": "search_locations",
  "description": "Search for locations within a region that exceed a specified temperature or heat index threshold. Useful for identifying heat hotspots.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "region": { "type": "string", "description": "Region name (e.g., 'Phoenix, AZ') or bounding box" },
      "threshold": { "type": "number", "description": "Temperature threshold in Celsius" },
      "metric": { "type": "string", "enum": ["temperature", "heat_index"], "default": "heat_index" }
    },
    "required": ["region", "threshold"]
  }
}
```

---

### `get_heat_events`

**Purpose**: Historical extreme heat events.

```json
{
  "name": "get_heat_events",
  "description": "Get historical extreme heat events for a region. Returns past heatwaves, record temperatures, and notable heat-related incidents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lat": { "type": "number" },
      "lng": { "type": "number" },
      "years_back": { "type": "integer", "description": "How many years of history to search", "default": 5 }
    },
    "required": ["lat", "lng"]
  }
}
```

---

### `query_evidence`

**Purpose**: RAG search over heat-safety documents.

```json
{
  "name": "query_evidence",
  "description": "Search heat-safety reference documents using semantic similarity. Returns relevant document chunks with source attribution.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Natural language query about heat safety" },
      "max_results": { "type": "integer", "description": "Maximum number of results", "default": 5 },
      "category": { "type": "string", "description": "Filter by document category", "enum": ["who_guidelines", "epa_standards", "city_plans", "research", "all"], "default": "all" }
    },
    "required": ["query"]
  }
}
```

**Response shape** (draft):
```json
{
  "results": [
    {
      "title": "WHO Heat and Health Guidance",
      "content": "When ambient temperatures exceed 30°C...",
      "source": "World Health Organization",
      "category": "who_guidelines",
      "relevance_score": 0.89,
      "document_id": "doc_001"
    }
  ],
  "receipt": {
    "tool": "query_evidence",
    "source": "local_rag",
    "embedding_model": "all-MiniLM-L6-v2",
    "query_time": "2026-08-05T14:01:23Z"
  }
}
```

---

## Evidence Receipt Standard

Every tool response includes a `receipt` object:

```json
{
  "receipt": {
    "tool": "tool_name",
    "source": "where_the_data_came_from",
    "query_time": "ISO-8601 timestamp",
    "cached": false,
    "confidence": "high | medium | low"
  }
}
```

This is the core differentiator. Judges see exactly where every number came from.

---

## Open Questions

- [ ] **Auth method**: API key in header? Query param? Bearer token? (Check docs when key arrives)
- [ ] **Rate limits**: How many requests per minute/second?
- [ ] **Credit cost per endpoint**: How many credits does each API call consume?
- [ ] **Hackathon credit allocation**: How many free credits for hackathon participants?
- [ ] **Forecast availability**: Is forecast data available via API, or only current observations?
- [ ] **Bounding box queries**: Can we query an area, or only point coordinates?
- [ ] **Environmental parameters**: Which additional parameters are available beyond temperature? (humidity, wind, UV, air quality?)
- [ ] **Heatmap generation**: Can we generate heatmaps via API, or only via dashboard?
- [ ] **Response shapes**: Validate actual JSON structure against docs on Day 1-2
- [ ] **Satellite/Street View Segmentation**: Available on hackathon tier? Could be a differentiator
