# Data Contract

Luna consumes the sanitized `GET /api/answer?question=<text>&mode=replay|live` payload from `app/server.py`. It does not call FortyGuard, NWS, GIS, or any provider directly.

## Core fields

`mode`, `visualization_source`, `observation_time`, `summary`, `conditions`, `why_this_answer`, `sources`, `heatmap`, `priority_location`, `ranked_candidates`, `nws_context`, `gis_context`, `urban_heat_brief`, `evidence_chain`, `error` may be absent/null.

`heatmap.features` is a GeoJSON feature array. Polygon temperature is read only from payload feature properties (`temperature_celsius`, `temperature`, `temp_celsius`, or `value`) and is not invented.

`conditions` may contain area mean/min/max/range, feature count, ranked candidates, ranking status/explanation, and `tie_threshold_celsius`. Ranking ordering is payload ordering; Luna never sorts or re-scores.

Candidates may have nullable coordinate, observed temperature, deltas, environmental fields, tile ID, and `candidate_context`. Missing values render as “—” or “Context unavailable.”

## Mode

- Replay is deterministic historical captured evidence; NWS current context is excluded.
- Live is an asynchronous latest-available provider workflow; Live errors remain Live errors and never reuse Replay geometry.
- UI clears layers at each request and ignores stale responses.

## Environmental parameter limitation

In Replay, candidate `observed_temp` is candidate-specific heatmap evidence. `heat_index`, `apparent_temp`, and `humidity` are presented with an explicit representative Replay context note because the current fixture historically supplies representative context. Live values are described as candidate-retrieved only when the Live payload provides them.

## GIS limitation

The frontend distinguishes successful park result (`available=true`, `inside_park` boolean), successful no-park result (`available=true`, `inside_park=false`), and unavailable (`available=false` or missing). Because the current backend defect may collapse a genuine Live parks failure into an empty result, this remains a known limitation; the frontend does not convert frontend failure into “no mapped park.” GIS always displays `used_in_decision=false`.
