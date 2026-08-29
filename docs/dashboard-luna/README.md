# Dashboard Luna

An isolated clean-sheet challenger for FortyGuard Hackathon ’26 Urban Heat Intelligence.

## Status

Lifecycle: **promoted Luna lineage → P1 (audience + map legibility) → P1-R1 (pre-freeze target Shape)**.

- P1 base: `bb6e1cc` (refinement/dash-v2-p1-map-legibility)
- P1 product commit: `c10ac26`
- P1-R1 branch: `refinement/dash-v2-p1-r1-prefreeze`
- P1-R1 status: **implemented as bounded refinement; NOT qualified/frozen/deployed**

See `docs/teaching/UHI-PRODUCT-NARRATIVE-P1R1-001.md` for the stabilized product thesis, evidence roles, temporal rules, and pre-freeze Shape.

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
