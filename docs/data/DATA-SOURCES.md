# Urban Heat Intelligence — Data Sources Reference

**Version:** 1.0.0
**Date:** 2026-08-26
**Owner:** urban-heat-intelligence

---

## Source Catalog

### FortyGuard (Primary — Required)

| Property | Value |
|----------|-------|
| Role | Thermal intelligence and hotspot detection |
| API Base | FortyGuard API |
| Endpoints | /v1/heatmap, /v1/env_params, /v1/system/fetch-api-key-usage |
| Premium | /v1/satellite, /v1/streetview, /v1/heat_intelligence |
| Resolution | 2m thermal mapping |
| Auth | FORTYGUARD_API_KEY |
| Pattern | Async: POST → activity_id → poll GET |
| Data Volume | 52B data points/day globally |

### NWS (Optional — Current Context)

| Property | Value |
|----------|-------|
| Role | Weather conditions and advisories |
| API | api.weather.gov (public, no key) |
| Endpoints | /points/{lat},{lon}, /gridpoints/{office}/{gridX},{gridY}/forecast |
| Data | Current conditions, alerts, forecasts |

### Phoenix/Maricopa GIS (DEFERRED — Not Integrated)

| Property | Value |
|----------|-------|
| Role | Local physical and cooling context |
| Status | DEFERRED — not integrated in current product |
| API | Open data portal |
| Layers | Vegetation, parks, canopy, cooling centres, demographics |

### NOAA (DEFERRED — Not Integrated)

| Property | Value |
|----------|-------|
| Role | Historical and climatological comparison |
| Status | DEFERRED — not integrated in current product |
| API | NOAA Climate Data Online |
| Data | 30-year normals, historical records, trends |

### Local News (NOT AUTHORIZED — Not Integrated)

| Property | Value |
|----------|-------|
| Role | Human-interest and community context |
| Status | NOT AUTHORIZED — not integrated in current product |
| Usage | Contextual only — never measurement |
