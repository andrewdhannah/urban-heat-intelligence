# Dashboard Luna

An isolated clean-sheet challenger for FortyGuard Hackathon ’26 Urban Heat Intelligence.

## Status

Lifecycle: **researched → designed → implemented → self-tested → comparison complete → challenger candidate**. This is not qualified, accepted, canonical, promoted, or submission-ready.

Base source SHA: `3134f288cc10792c66fa7839d34f1abe63ba0206`
Challenger branch: `dashboard-luna-cleansheet`

## Run

The normal application serves `app/static`, so Luna is intentionally not wired into `/`. Start the existing backend in one terminal:

```bash
python3 app/server.py
```

Then serve Luna in another terminal:

```bash
python3 app/dashboard-luna/preview_server.py
```

Open `http://localhost:8090/`. This same-origin challenger preview imports `get_agent_result()` and `build_visualization_payload()` from the canonical `app.server` and serves `/api/answer` and `/api/config` without modifying production serving. `serve_preview.py` remains available as a static-only asset server.

## Boundaries

- `app/static/` is untouched control material.
- No analytical backend or provider contract is duplicated.
- FortyGuard remains primary decision evidence.
- NWS is current supplemental context in Live and explicitly excluded in Replay.
- Phoenix GIS is contextual and `used_in_decision=false`.
- Replay and Live geometry never mix.
- The frontend treats Replay environmental parameters as representative context, not independent candidate measurements.

## Files

- `index.html`: semantic dashboard shell and compatibility hooks.
- `css/`: tokenized visual system and responsive rules.
- `js/dashboard.js`: API lifecycle, safe rendering, map lifecycle, candidate synchronization, brief and evidence rendering.
- `serve_preview.py`: isolated static preview helper.

See the remaining files in this directory for contracts, architecture, QA, integration, and promotion documentation.
