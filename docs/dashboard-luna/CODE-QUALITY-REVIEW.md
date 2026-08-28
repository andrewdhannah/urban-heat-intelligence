# Code Quality Review

## Approximate LOC

- `js/dashboard.js`: ~220 lines
- `css/tokens.css`: ~20 lines
- `css/dashboard.css`: ~20 dense stylesheet lines / ~230 logical declarations
- `css/responsive.css`: ~3 dense media-rule lines
- `index.html`: ~55 logical lines
- `serve_preview.py`: ~18 lines

## Review

- External dependencies: existing Leaflet CDN, CARTO tiles, Google Fonts; no new package/build dependency.
- Duplicated logic: limited formatting/render helpers; no analytical logic duplicated.
- Global state: one bounded `state` object plus DOM references by ID.
- Event lifecycle: listeners attached once on DOMContentLoaded; one map instance retained.
- Map lifecycle: GeoJSON and markers removed before each render; no old-mode geometry survives.
- DOM sanitation: provider strings use `textContent`; no provider data in `innerHTML` except rank marker markup generated from numeric payload rank and escaped through DOM-derived `outerHTML`.
- Error handling: aborts stale requests, bounded Live failure, optional context stays non-fatal.
- Accessibility hooks: semantic sections, labels, `aria-live`, `aria-pressed`, keyboard cards, focus ring, reduced motion.
- CSS token usage: core colors/spacing/type/elevation are tokenized; external Leaflet styles remain library-owned.
- Hard-coded data scan: no candidate values, dates, feature counts, park names, or credentials. The default question and canonical threshold are intentional contract constants.

Bounded remediation fixed candidate DOM insertion, canonical `average_temperature` extraction, near-tie hero wording, Replay environmental-context placement, and GIS no-park display. The implementation remains one bounded module; split before production promotion if selected.
