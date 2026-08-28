# Integration Guide

## Current server

`app/server.py` serves the incumbent `app/static` root and exposes:

- `GET /api/answer?question=<text>&mode=replay|live`
- `GET /api/config` for non-sensitive client configuration

NWS arrives through server-side composition in `nws_context`; GIS arrives through candidate context/result composition; Brief arrives in `urban_heat_brief`; audit data arrives in `evidence_chain`.

## Wire Luna

1. Keep `app/server.py` and `app/static/` unchanged for challenger evaluation.
2. After owner approval, either change the static directory to `app/dashboard-luna` (Strategy A) or add a feature-flagged static root (Strategy B).
3. Serve `index.html`, `css/`, and `js/` from the selected root.
4. On initialization, call `/api/answer` with the default question and `mode=replay`.
5. On mode click, abort the prior fetch, clear map layers, show target-mode loading, and request `/api/answer` with the same question and new mode.
6. Ignore any response whose sequence ID is older than the current request.
7. Initialize Leaflet once; replace only the current GeoJSON and candidate markers.
8. Render candidates in payload order; never re-rank.
9. Render Brief claims and evidence chain from payload only.
10. Render errors as bounded status; Live failure offers an explicit Replay switch and never auto-falls back.

| Backend field | Luna component |
|---|---|
| `mode`, `visualization_source` | Data mode, mode badge, map source |
| `observation_time` | Observation card |
| `summary`, `why_this_answer` | Answer rail / Brief |
| `conditions` | Stats and ranking callout |
| `heatmap.features` | GeoJSON measured field |
| `ranked_candidates` | Cards and markers |
| `candidate_context` | Local context panel |
| `nws_context` | Brief weather section / Replay exclusion |
| `urban_heat_brief` | Brief claims |
| `evidence_chain` | Audit drawer |
| `error` | Bounded error state |

## Preview

The included `preview_server.py` serves Luna and the canonical `/api/answer` and `/api/config` endpoints at `http://localhost:8090/` using imports from `app.server`; no analytical backend is duplicated. `serve_preview.py` is static-only and is useful when testing assets without API calls.
