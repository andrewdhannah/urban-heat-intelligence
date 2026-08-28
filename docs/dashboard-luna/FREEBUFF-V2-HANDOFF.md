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
- Closeout refinements: intervention-effect guardrail now takes precedence over canopy/parks intents; explicit show-live/show-replay mode intents are supported; comparison answers disclose FortyGuard only; unavailable canopy is stated textually.
- Source-disclosure remediation: source controls now support hover, focus, click/tap pinning, outside click, and Escape; FortyGuard copy is mode-aware; active NWS disclosure is rendered only for usable Live context; analyst WHY text is intent-specific.
- Limitations: Live credential and automated axe audit remain unavailable; browser verification is deferred to Librarian when the preview process is unavailable; backend lineage remains 3134f28 until independent reconciliation.

- Micro-remediation parent: `557f2e3a7851da139d0c723260310065737cea62`. This child adds the missing explicit mode registry entry and replaces unavailable canopy `—` output with truthful text. Playwright execution is deferred to Librarian verification if unavailable here.
