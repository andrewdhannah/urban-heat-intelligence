# Field to UI Mapping

| Payload field | Component / label | Role | Null/unavailable behavior |
|---|---|---|---|
| `mode` | Data mode, mode badge | epistemic mode | loading/error state |
| `visualization_source` | map source label | provenance | never substitute other mode |
| `observation_time` | Observation card | temporal | “Unavailable” |
| `summary` | Answer rail | narrative | bounded fallback |
| `conditions.area_mean_temperature_celsius` | Area mean | measured summary | em dash |
| `conditions.area_temperature_range_celsius` | Area range | measured summary | em dash |
| `conditions.feature_count` | Cells | measured coverage | em dash |
| `conditions.ranking_status` | Ranking callout | derived comparison | no callout without candidates |
| `heatmap.features` | measured map | FortyGuard decision evidence | empty field message |
| `ranked_candidates` | candidate cards/markers | FortyGuard ordering | no candidates message |
| `candidate_context.canopy` | local context rows | Phoenix GIS context | unavailable, never inferred |
| `candidate_context.parks` | local context rows | Phoenix GIS context | unavailable vs no-park preserved where payload distinguishes |
| `nws_context` / Brief weather section | Brief | Live supplemental context / Replay exclusion | unavailable disclosure |
| `urban_heat_brief` | Brief sections and claims | composed evidence narrative | brief unavailable |
| `evidence_chain` | audit drawer | provenance | no events message |
| `error` | status region | bounded failure | explicit Try Replay only for Live |
