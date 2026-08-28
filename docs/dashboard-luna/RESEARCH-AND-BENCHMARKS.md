# Research and Benchmarks

Research was performed 2026-08-27. External source material is inspiration/context, not application evidence. No external values are activated in Luna.

## Authoritative references

- FortyGuard Hackathon ’26: https://www.fortyguard.com/hackathon26 — positioning centers hyper-local temperature intelligence and urban-heat problem solving.
- FortyGuard: https://www.fortyguard.com/ — product/company positioning around temperature intelligence.
- NWS Phoenix heat page: https://www.weather.gov/psr/Heat — official heat communication and distinction between complementary HeatRisk and official watches/warnings/advisories.
- NWS HeatRisk: https://www.wpc.ncep.noaa.gov/heatrisk/ — supplementary seven-day risk forecast, distinct from an observation.
- City of Phoenix Office of Heat Response and Mitigation: https://www.phoenix.gov/administration/departments/heat.html — local heat response/mitigation terminology and civic audience.
- City of Phoenix Heat Response Plan: https://www.phoenix.gov/administration/departments/heat/heat-response-programs/heat-response-plan.html — action-oriented municipal framing.
- Maricopa County Heat Surveillance: https://www.maricopa.gov/1858/Heat-Surveillance — weekly surveillance and annual mortality/morbidity reporting; research-only here.
- NOAA/NCEI Storm Events Database: https://www.ncei.noaa.gov/stormevents/ — historical event records; not active in runtime.
- USGS Annual NLCD Fractional Impervious Surface: https://www.usgs.gov/centers/eros/science/annual-nlcd-fractional-impervious-surface — physical context concept; not active in runtime.

## Comparative products

| Example | Observed strengths | Cognitive load / caution | Luna takeaway |
|---|---|---|---|
| NWS Phoenix Heat page | Strong official language, time and warning distinction | Multiple products can be hard to compare | Keep observation, context, and warning semantics separate |
| NWS HeatRisk | Clear color-number scale and forecast framing | Risk scale may be mistaken for measured temperature | Never apply HeatRisk categories to FortyGuard cells |
| ArcGIS UHI tutorial/map | Spatial analysis is legible and geographic | GIS layers can overwhelm novice viewers | Quiet basemap, one dominant measured layer |
| NOAA Heat Watch / UHI Mapping Campaign | High-resolution map storytelling and public communication | Modelled products can look more certain than they are | Label source and evidence type at the point of use |
| San Diego Climate Resilience web map | Combines exposure, vulnerability, and risk layers | Layer stacking creates attribution ambiguity | Separate primary field from contextual layers |
| Maricopa County Heat Surveillance | Strong public-health temporal framing | Epidemiological context is not a site-level intervention rank | Reserve public-health history for a future adapter |
| WRI city climate risk dashboard | Cross-theme city decision framing | KPI density and theme switching slow first comprehension | One question and one primary workflow |
| USGS NLCD data products | Clear physical-context provenance | Raster resolution/date can be missed in visual UI | Show reference period and provider, never infer causality |

## Inference
- High-stakes environmental interfaces work best when the map answers “where” and a restrained side rail answers “so what.”
- Official weather products model useful temporal/provenance distinctions, but their risk taxonomies should not be imported into a FortyGuard thermal ranking.
- Local Phoenix terminology favors heat response, mitigation, shade, and operations rather than generic “AI recommendations.”

## Design decisions
- Use a measured-field header and source legend.
- Put Replay/Live mode and observation time above the map.
- Make near-tie status a large textual callout.
- Use NWS/GIS as explicit context-only surfaces.
- Keep NOAA, USGS, Maricopa and historical sources documented as future attachments only.
