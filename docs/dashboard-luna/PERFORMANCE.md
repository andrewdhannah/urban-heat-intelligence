# Performance

No build step and no framework. Runtime dependencies are the already-used Leaflet browser library plus public basemap/font assets. One Leaflet map instance is retained; one GeoJSON layer and one marker per candidate are retained. `preferCanvas` reduces SVG DOM pressure for hundreds of polygons. Old layers are explicitly removed on every mode/query change.

The request sequence and AbortController prevent stale responses and duplicate visual updates. DOM lists are replaced as bounded sections rather than appended indefinitely. Future profiling should measure first meaningful map paint, replay render time, repeated mode switches, resize, and drawer open at 367 features.
