# Current Dashboard Comparison

Comparison completed after `DESIGN-FREEZE-V1.md`.

Scores are design-review estimates from repository structure and incumbent inspection, not qualification results. Luna was not judged against an incumbent screenshot as a template.

| Dimension | Current | Luna | Note |
|---|---:|---:|---|
| Immediate comprehension | 7 | 9 | Luna leads with one decision sentence and map |
| Information architecture | 7 | 9 | Explicit glance/analysis/audit layers |
| Visual hierarchy | 6 | 9 | Luna uses map + answer rail |
| Map usefulness | 7 | 9 | Candidate/text synchronization designed in |
| FortyGuard prominence | 8 | 9 | Both preserve primary role; Luna repeats it at map/rail |
| Near-tie communication | 8 | 9 | Luna makes callout prominent and avoids rank emphasis |
| Candidate comparison | 7 | 9 | Luna's cards are purpose-built |
| Replay/Live distinction | 8 | 9 | Luna gives modes explanatory copy and clears old state |
| Observation-time clarity | 7 | 9 | Luna elevates time into observation card |
| GIS context clarity | 7 | 9 | Luna labels context-only and unavailable explicitly |
| NWS context clarity | 8 | 9 | Replay exclusion is visible in Brief/evidence |
| Brief usability | 7 | 9 | Sectioned claims over text dump |
| Provenance | 8 | 9 | Timeline and claim metadata |
| Judge/demo value | 7 | 9 | Natural three-minute narrative |
| Accessibility | 6 | 8 | Luna adds keyboard cards, labels, status, reduced motion |
| Responsive behavior | 6 | 8 | Intentional map/rail/list breakpoints |
| Code architecture | 7 | 8 | Luna isolated and bounded, but currently one JS module |
| Maintainability | 7 | 8 | Minimal dependency/build burden |
| Testability | 7 | 7 | Stable IDs retained; dedicated browser tests still needed |
| Performance | 7 | 8 | Canvas + layer cleanup |
| Cognitive load | 6 | 8 | Progressive disclosure |

## Current strengths

The incumbent has mature backend-compatible hooks, existing behavioral test expectations, and a clear API contract. Its server already enforces important mode and source boundaries.

## Luna strengths

Map dominance, explicit observation time, near-tie treatment, source hierarchy, progressive evidence, and demo-friendly flow.

## Luna weaknesses

The prototype currently concentrates behavior in one JS file, relies on external Leaflet/font/basemap assets, and needs a same-origin preview wiring path plus real browser QA. It does not solve the backend GIS failure-collapse defect.

## Clear winner

No unconditional winner. Luna is the stronger visual decision experience; Current remains the lower-risk already-served implementation. **Recommendation: synthesize after independent QA**, not automatic replacement.
