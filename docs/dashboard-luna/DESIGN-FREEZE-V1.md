# Dashboard Luna — Design Freeze V1

**Design state:** independent clean-sheet freeze, created before inspecting the incumbent visual implementation.

## Product mental model

Luna is a **thermal field → candidate cluster → evidence** decision surface. It does not prescribe a project or calculate intervention efficacy. FortyGuard observations establish the thermal ordering; Phoenix GIS and NWS add context without changing that ordering.

## Information architecture

1. **Decision header:** Phoenix, user question, data mode, observation time, freshness status.
2. **Decision stage:** dominant measured heat map with a short answer rail and explicit source legend.
3. **Comparison stage:** candidate cards and a near-tie statement that prevents false precision.
4. **Context stage:** candidate-specific canopy/park context and environmental parameters with role labels.
5. **Brief stage:** concise evidence-backed narrative with claim-level disclosure.
6. **Audit stage:** expandable evidence timeline and source-role summary.

## Primary workflow

On load, Replay runs automatically. A user reads the answer, locates the top thermal cluster, compares the three deterministic ranks, opens a candidate, then opens the brief or evidence trace. Mode switching clears old map layers before fetching the target mode; Live failure remains Live unavailable and offers an explicit Replay action.

## Map strategy

The map is the primary analytical surface. Heatmap polygons are rendered as a restrained sequential thermal field over a quiet basemap. Candidate markers are synchronized with textual cards. The map has a textual candidate alternative, so map-only information is never required. Polygon clicks show the measured cell value, not a synthetic risk category.

## Candidate strategy

Show up to three payload-ranked candidates in a horizontal comparison rail on desktop and a vertically ordered, compact list on mobile. Rank numbers remain deterministic, but near-tie candidates share visual emphasis. No context field re-ranks candidates.

## Evidence and provenance strategy

Use progressive disclosure. The brief leads with claims, each tagged by provider and role. The evidence drawer turns canonical step types and actual repeated events into a readable timeline. Source roles are expressed by labels and structure, never color alone.

## Mode strategy

Replay and Live are a segmented **Data mode** control with explanatory copy. Replay says reproducible historical capture; Live says latest available provider workflow. Mode, source, and observation time remain visible at all times. Old-mode geometry is removed before target-mode loading.

## Responsive strategy

Desktop uses a two-column decision stage: map first, answer rail second. At tablet width the rail drops below the map. At mobile, the map remains prominent but bounded, candidate comparison becomes a concise list, and audit surfaces become full-width disclosures. No horizontal scrolling is permitted.

## Visual direction

Warm mineral surfaces, ink typography, cool civic blue for decision evidence, amber/terracotta for measured heat, and green/blue-gray for contextual layers. The visual language is municipal intelligence rather than neon AI: clear borders, editorial type scale, compact labels, and generous map area.
