# Map Architecture

Luna keeps the existing Leaflet dependency and uses `preferCanvas` for GeoJSON rendering. CARTO light-no-labels is deliberately quiet so the measured field remains primary.

## Layers

1. Basemap: contextual geography only.
2. FortyGuard GeoJSON polygons: measured field, sequential mineral palette.
3. Candidate markers: numbered DOM markers synchronized to cards.

Old GeoJSON and markers are removed before each render. A single map instance survives requests; this avoids repeated controls and memory growth. Bounds come from the current payload's heatmap only. Coordinates are interpreted as `[longitude, latitude]` for candidate arrays and standard GeoJSON order.

Polygon interaction displays the measured cell value. It does not create a risk classification. Candidate cards are keyboard-focusable alternatives to marker-only interaction.
