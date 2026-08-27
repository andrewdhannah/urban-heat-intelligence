# Sprint Brief — LEVEL A: Phoenix GIS Context Shape

**Project:** urban-heat-intelligence
**Sprint ID:** LEVEL-A-GIS-CONTEXT
**Authorization:** Owner Disposition (2026-08-27)
**Status:** AUTHORIZED
**Branch:** hackathon-expansion

---

## Objective

Attach authoritative Phoenix tree-canopy and parks context to the existing ranked FortyGuard candidates. The expansion must preserve all existing thermal analysis semantics, evidence chains, and qualification meaning. GIS context is additive and contextual—GIS MUST NOT silently become part of the ranking.

## Composition

```
THERMAL ANALYSIS SHAPE
        +
PHOENIX GIS CONTEXT SHAPE
        =
EXPANDED UHI CANDIDATE
```

Do not reinterpret the original thermal Shape.

## Required Amendments (Owner-Specified)

### Amendment 1: Sealed Files Modified

The preflight report claimed `SEALED_SURFACES_TOUCHED: NONE` while modifying `controller.py` and `brief.py`. The correct claim:

```
SEALED_FILES_MODIFIED:
    controller.py
    brief.py

SEALED_CONTRACTS_REDEFINED:
    false
```

Append-only source modification is still modification.

### Amendment 2: Evidence Chain Composition

Do NOT extend the existing 8-node evidence chain in place. Use composition:

```
evidence:
    thermal: [existing 8 nodes, unchanged]
    context: [new GIS evidence segment]
```

or:

```
context_evidence_chain: [...]
```

The existing `evidence_chain` field remains exactly as-is.

### Amendment 3: Separate GIS Fixture Boundary

Phoenix GIS fixtures must NOT be placed in `fixtures/fortyguard/integrity-manifest.json`. Create:

```
fixtures/phoenix-gis/integrity-manifest.json
```

Each provider/evidence Shape owns its own fixture integrity boundary.

### Amendment 4: Conservative Park Claims

Do NOT claim "nearest park at N metres" unless distance calculation is explicitly implemented and tested. Use:

- "inside a mapped City park"
- "mapped parks within the configured search radius"

---

## Tree Canopy

Source: Phoenix Urban Heat Island and Tree Canopy Equity Analysis
Provider: City of Phoenix / Maricopa Association of Governments

Required candidate context:
- census_tract_geoid
- tree_canopy_pct
- source_provider
- dataset
- reference_period/date
- query_method
- retrieved_at
- used_in_decision = false

User-facing language MUST make granularity explicit:
- "The candidate lies within a census tract with X% tree canopy in the referenced City/MAG dataset."
- Do NOT imply parcel-level canopy, candidate-point canopy, current canopy measurement, or causal relationship to FortyGuard temperature.

Do NOT use heat_equity_priority_score, median_income, or other demographic/equity fields in Level A.

Do NOT make Phoenix GIS land-surface temperature a competing user-facing thermal measurement.

## Parks

Source: City of Phoenix mapped park data

Required first-order context:
- inside_park
- park_name
- park_type
- park_acres

Nearby parks MAY be provided using a bounded configured search radius.

Permitted language:
- "This candidate lies inside [PARK]."
- "[PARK] and other mapped City parks are within the configured nearby-search area."

Do NOT infer shade, vegetation, cooling effectiveness, or intervention suitability.

## Evidence Model

PRESERVE existing top-level thermal evidence chain semantics. The existing eight thermal nodes remain unchanged.

Introduce an additive contextual evidence structure:
- `context_evidence_chain` (new field)
- Context segment may include: canopy_request, canopy_result, parks_request, parks_result, context_enrichment_result
- Every contextual evidence node must carry sufficient provider, dataset, timing, and mode provenance.

## Replay

- Live: query City of Phoenix GIS services.
- Replay: zero live GIS network calls. Capture genuine GIS responses for candidate geography.

Create:
- `fixtures/phoenix-gis/canopy.json`
- `fixtures/phoenix-gis/parks.json`
- `fixtures/phoenix-gis/integrity-manifest.json`

## Brief

Add LOCAL CONTEXT section after existing thermal/decision material.

Claims must distinguish:
- FortyGuard: thermal authority, ranking evidence
- City/MAG: canopy context
- City of Phoenix: parks context

Every GIS claim: `used_in_decision = false`

The Brief must explicitly state that GIS context does not alter the current thermal ranking.

## UI

Add concise context to candidate presentation:
- CANOPY CONTEXT: X% tree canopy, Census tract context, City/MAG · reference year
- PARK CONTEXT: Inside: <park> | No mapped park at candidate

Preserve visual hierarchy: FortyGuard thermal result FIRST, GIS context SECOND.

## Implementation Truth

Expected:
```
sealed_files_modified:
    controller.py
    brief.py
    possibly presentation/server paths

sealed_contracts_redefined:
    false
```

## Tests

Additive tests must cover:
- canopy point-in-polygon success
- tract-level semantic labeling
- parks inside result
- parks outside result
- nearby parks bounded query
- canopy unavailable
- parks unavailable
- both GIS sources unavailable
- malformed provider result
- Live GIS behavior
- Replay zero GIS network
- fixture integrity
- existing thermal ranking unchanged
- existing eight-node evidence chain unchanged
- GIS context used_in_decision=false
- Brief LOCAL CONTEXT provenance
- browser rendering
- no unsupported claims

Existing 91 tests must remain green.

## Failure Behavior

- Canopy failure: parks may remain.
- Parks failure: canopy may remain.
- Both fail: thermal product still operates normally.

GIS failure MUST NOT:
- alter ranking
- substitute fake context
- convert Replay into Live
- suppress valid FortyGuard results

## Promotion Conditions

Implementation does NOT equal promotion. Expanded candidate remains experimental until:
- implementation complete
- additive tests pass
- existing 91 tests pass
- replay deterministic
- fixture integrity verified
- browser smoke passes
- claims audited
- provenance complete
- QA-Pilot qualifies new behavior
- Owner accepts promotion

Until then: `c13d8ea` remains the submission fallback.

## Files Modified

- `src/agent/controller.py` — add GIS context enrichment (append-only)
- `src/agent/brief.py` — add LOCAL CONTEXT section (append-only)
- `src/tools/gis_context.py` — NEW: Phoenix GIS context module
- `fixtures/phoenix-gis/` — NEW: GIS fixtures
- `tests/test_level_a_gis.py` — NEW: Level A tests
- `app/server.py` — add GIS context to visualization payload
- `app/templates/index.html` — add GIS context UI section
- `app/static/style.css` — add GIS context styling

## Forbidden

- Do NOT modify the existing 8-node evidence chain structure
- Do NOT add GIS nodes to the thermal evidence chain
- Do NOT alter thermal ranking logic
- Do NOT use GIS land-surface temperature as a competing thermal measurement
- Do NOT imply parcel-level canopy or current measurements
- Do NOT claim distance without explicit calculation and testing
- Do NOT place GIS fixtures in FortyGuard integrity manifest
