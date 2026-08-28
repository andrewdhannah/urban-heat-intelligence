# FreeBuff Luna V2 Handoff

- Branch: `dashboard-luna-cleansheet`
- Starting SHA: `dc6d2d83f63c45812984a7dfd7cf0d6ffe27f1da`
- Runtime: `app/dashboard-luna/index.html`, `css/`, `js/dashboard.js`, `preview_server.py`
- Tests: `tests/test_dashboard_luna_browser.py`
- Docs: `docs/dashboard-luna/` V2 plan, analyst contract, source registry, map focus, and updated handoff
- Preview: `python3 app/dashboard-luna/preview_server.py`; `http://127.0.0.1:8090/`
- Backend: canonical `app.server` reused by preview; no analytical changes
- External runtime: Leaflet CDN and OpenStreetMap tiles; no key required
- Excluded: `app/static/`, `hackathon-expansion`, credentials, generated caches, browser environments
- Limitations: Live credential and automated axe audit remain unavailable; backend lineage remains 3134f28 until independent reconciliation.
