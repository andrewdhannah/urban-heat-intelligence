# Security Boundary

The browser only calls the sanitized application endpoint `/api/answer` and optionally relies on same-origin static serving. FortyGuard credentials remain server-side in `app/server.py` and the adapter; no browser-side provider calls exist. `/api/config` may expose only non-sensitive basemap configuration if the approved integration uses it.

Remote/provider-derived values are inserted with `textContent`, not interpolated into HTML. Leaflet marker labels use rank values from structured payloads; no credential or raw provider internals are logged or rendered. External Leaflet/CARTO/Google Fonts assets are public dependencies and can be self-hosted during deployment if network policy requires.
