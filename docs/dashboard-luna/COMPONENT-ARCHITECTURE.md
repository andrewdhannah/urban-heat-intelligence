# Component Architecture

The implementation is framework-free ES module-ready static HTML/CSS/JS for low operational risk.

- `index.html`: semantic landmarks, stable behavior hooks, no analytical data.
- `css/tokens.css`: design tokens and base accessibility rules.
- `css/dashboard.css`: component styles.
- `css/responsive.css`: breakpoint and reduced-motion behavior.
- `js/dashboard.js`: small state object, API requests, stale-response cancellation, safe DOM construction, Leaflet lifecycle, candidate/marker sync, Brief, context, evidence.
- `serve_preview.py`: isolated static asset server only.

Global state is limited to mode, request sequence, AbortController, map, current layer, marker map, and current candidate array. Every new request removes old layers and aborts the previous request. Provider-derived strings use `textContent`; the only map popup-like content uses DOM nodes, not untrusted HTML.

Future adapters can expose normalized `ContextSection` objects without changing the thermal render path.
