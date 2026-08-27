# Urban Heat Brief — Specification

**Version:** 1.1.0
**Date:** 2026-08-26
**Owner:** urban-heat-intelligence
**Authority:** Owner expansion directive
**Supersedes:** v1.0.0 (added near-tie semantics, revised source hierarchy, four-question composition structure)

---

## 1. Purpose

The Urban Heat Brief is a short, human-readable weather-news-report generated entirely from attributable data. It is a **first-class output** of the agent, alongside the analytical decision view.

**Target consumers:** Planners, emergency managers, journalists, councillors, residents.

---

## 2. Governing Rules

### 2.1 The Narrative Evidence Rule

> **Narrative may simplify evidence. It may never invent or blur evidence.**

Each sentence in the Brief must be traceable to the evidence graph. A claim that cannot be attributed to a specific source at a specific timestamp is forbidden.

### 2.2 The Source Hierarchy

The Brief is composed from four questions, each answered by the appropriate source layer:

```
DECISION EVIDENCE
    FortyGuard — What does the thermal field show?

OFFICIAL CURRENT CONTEXT
    NWS — What is happening in Phoenix more broadly right now?

OPTIONAL AUTHORITATIVE/LOCAL CONTEXT
    Phoenix/Maricopa GIS — What physical/cooling context exists?
    NOAA — How does this compare historically?

HUMAN CONTEXT
    Reputable local reporting — What is the human consequence?
```

| Layer | Source | Product Role | Narrative Role |
|-------|--------|-------------|----------------|
| Decision evidence | FortyGuard | Primary thermal intelligence | Temperature measurements, heat burden rankings, hotspot identification |
| Official current context | NWS | Current weather/advisory corroboration | Official weather conditions, advisories, warnings |
| Local physical context | Phoenix/Maricopa GIS | Physical/cooling infrastructure | Vegetation, parks, canopy, cooling infrastructure |
| Historical context | NOAA | Climatological comparison | Historical comparisons, climate normals, trend context |
| Human context | Reputable local reporting | Community impact | Cooling centre activity, city response, human stories |

**Critical rule:** News never participates in the mathematical ranking. News explains human consequence; authoritative data establishes measurements.

### 2.3 Source Separation Rules

| Rule | Correct Pattern | Forbidden Pattern |
|------|-----------------|-------------------|
| Temperature belongs to measurement sources | "FortyGuard observed 44.2°C" | "It is 44.2°C" (unattributed) |
| News explains human consequence, never measurements | "Local reporting describes cooling-centre activity" | "The temperature is 44.2°C" (sourced from news) |
| Historical comparison requires NOAA | "Compared with NOAA observations, today is X°C above average" | "This is unusually hot" (no source) |
| Absent source = absent claim | [NWS section omitted] | "NWS reports clear skies" (invented when NWS unavailable) |
| Near-tie candidates: say so honestly | "Three locations show effectively equivalent thermal burden" | "42.0525°C meaningfully outranks 42.0521°C" |

### 2.4 What News Can and Cannot Provide

**News CAN provide (contextual evidence):**
- Cooling centre openings and locations
- City heat-response activity
- School/outdoor-program changes
- Public-health messaging
- Power demand issues
- Local impacts of the heat event

**News CANNOT provide (must come from authoritative sources):**
- Temperature measurements
- Scientific claims about heat intensity
- Analytical rankings or comparisons
- Historical climatological context

**The distinction:** News explains human consequence. Authoritative data establishes measurements.

---

## 3. Brief Structure

### 3.1 Template

```
{CITY} Urban Heat Brief — {TIME}

{FORTYGUARD_SECTION}

{NWS_SECTION}

{GIS_SECTION}

{NOAA_SECTION}

{NEWS_SECTION}

{DECISION_SECTION}

Sources: {SOURCE_LIST}
```

### 3.2 Section Definitions

#### FortyGuard Section (Required)

```text
FortyGuard identifies the highest thermal burden in the queried {AREA} near
[location], where observed temperature is {TEMP}°C, {DELTA}°C above the area
average. Environmental conditions at the selected location produce an apparent
temperature of {APPARENT_TEMP}°C.
```

**Attributable claims:**
- Location of highest thermal burden → FortyGuard heatmap
- Observed temperature → FortyGuard env_params
- Area average → FortyGuard heatmap aggregate
- Apparent temperature → FortyGuard env_params (heat_index or apparent_temp)

#### NWS Section (Conditional — present only if NWS data available)

```text
NWS reports [current condition/advisory]. [Additional NWS detail if available.]
```

**Attributable claims:**
- Current condition → NWS current conditions API
- Advisory/warning → NWS alerts API

**If NWS unavailable:** Section is omitted entirely. No invented weather conditions.

#### GIS Section (Conditional — present only if GIS data available)

```text
City GIS shows [relevant vegetation/park/canopy context].
```

**Attributable claims:**
- Vegetation/park proximity → City GIS layer
- Canopy coverage → City GIS layer

**If GIS unavailable:** Section is omitted entirely. No invented physical context.

#### NOAA Section (Conditional — present only if NOAA data available)

```text
Compared with historical NOAA observations, today's conditions are [contextual statement].
```

**Attributable claims:**
- Historical comparison → NOAA climate data
- Deviation from normal → NOAA climate normals

**If NOAA unavailable:** Section is omitted entirely. No invented historical context.

#### News Section (Conditional — present only if local news available)

```text
Local reporting describes [human consequence / community context].
```

**Attributable claims:**
- Cooling centre activity → local news source
- City heat-response activity → local news source
- Community impact → local news source

**If news unavailable:** Section is omitted entirely. No fabricated human-interest context.

**Critical rule:** News provides context about human consequence, never measurements. "Local reporting describes cooling-centre activity near downtown" is correct. "The temperature is 44.2°C" sourced from a news article is forbidden.

#### Decision Section (Required)

Two cases:

**Case 1 — Clear ranking (score difference > threshold):**

```text
Decision: Of the three highest-burden locations examined, {LOCATION_A} warrants
first investigation for cooling intervention because [evidence-based reason].
```

**Case 2 — Near-tie (candidates thermally indistinguishable):**

```text
Decision: Three locations show effectively equivalent thermal burden in this
observation. FortyGuard identifies them as the highest-burden candidates, but
thermal evidence alone does not support a meaningful distinction between them.
Additional local context would be needed before selecting one intervention
location over another.
```

**Attributable claims:**
- Top-3 ranking → Agent priority scoring (SPEC-009)
- Selection rationale → Agent decision logic (SPEC-010)
- Near-tie detection → Score difference below significance threshold

**Near-tie rule:** It is better to say "thermally equivalent" than to falsely pretend that 42.0525°C meaningfully outranks 42.0521°C. Intellectual honesty strengthens the product's credibility.

#### Source List (Required)

```text
Sources: FortyGuard · NWS · City of Phoenix GIS · NOAA · Local reporting
```

List only sources actually consulted. If a source was unavailable, omit it from the list.

---

## 4. Narrative Composition Rules

### 4.1 Simplification Allowed

| Original Evidence | Acceptable Narrative |
|-------------------|---------------------|
| FortyGuard heatmap: 367 thermal features, top pixel at 44.2°C | "FortyGuard identifies the highest thermal burden near [location] at 44.2°C" |
| env_params: apparent_temp=47.1°C, humidity=12%, wind=3km/h | "Environmental conditions produce an apparent temperature of 47.1°C" |
| NWS: EXCESSIVE HEAT WARNING in effect through 8PM MST | "NWS reports an Excessive Heat Warning in effect" |

### 4.2 Simplification Forbidden

| Original Evidence | Forbidden Narrative |
|-------------------|---------------------|
| FortyGuard: 367 thermal features | "Hundreds of dangerous hotspots" (rounding loses precision) |
| NWS: heat advisory | "Dangerous conditions" ( editorializing beyond source) |
| NOAA: 2°C above 30-year average | "Unprecedented heat" (not supported by data) |

### 4.3 Conditional Composition

The Brief is composed from whatever sources are available. Missing sources produce missing sections — not invented content.

**Full brief:** FortyGuard + NWS + GIS + NOAA + News context
**Partial brief:** FortyGuard + NWS (GIS, NOAA, and News unavailable)
**Minimum brief:** FortyGuard only (all other sources unavailable)

The minimum brief is still useful. It provides thermal intelligence with attribution. The additional sources enrich context but are not required for the Brief to exist.

**Near-tie case:** When candidates are thermally indistinguishable, the Brief says so honestly. The decision section uses the near-tie template rather than fabricating a distinction.

---

## 5. Output Modes

### 5.1 Chat Output

The Brief is generated as a chat response when the user asks for a summary, report, or brief. The agent composes the Brief from its current evidence context.

### 5.2 Dashboard Output (Future)

If displayed in the UI, the Brief renders as a styled card with source attribution links. Each source name links to the underlying evidence.

### 5.3 Export Output

The Brief can be exported as plain text or markdown for use in reports, emails, or social media.

---

## 6. Evidence Graph Traceability

Every claim in the Brief must map to an entry in the evidence log:

```json
{
  "claim": "Observed temperature is 44.2°C near downtown Phoenix",
  "source": "fortyguard",
  "tool": "get_heatmap",
  "timestamp": "2026-08-26T14:15:00Z",
  "receipt_id": "fg-heatmap-20260826-141500"
}
```

The agent must maintain this mapping internally. If a claim cannot be mapped, it must not appear in the Brief.

---

## 7. Failure Modes

| Failure | Brief Behavior |
|---------|---------------|
| FortyGuard unavailable | Brief cannot be generated. Error message instead. |
| NWS unavailable | NWS section omitted. Brief continues with remaining sources. |
| GIS unavailable | GIS section omitted. Brief continues with remaining sources. |
| NOAA unavailable | NOAA section omitted. Brief continues with remaining sources. |
| All non-FortyGuard sources unavailable | Minimum brief: FortyGuard only |
| Conflicting sources (e.g., NWS timestamp differs from FortyGuard) | Disclose disagreement rather than silently reconcile. "NWS reports X while FortyGuard observes Y." |
| Stale source | Disclose age. "FortyGuard data from [time] (X minutes old)." |

---

## 8. Relationship to Existing Artifacts

| Existing Artifact | Relationship |
|-------------------|-------------|
| DEMO-SCRIPT.md | Heat Brief replaces Scenario 4 (city operations) as the primary narrative output |
| PITCH.md | Brief is the concrete implementation of "evidence-backed heat decision support" |
| UHI-SPEC-011 (claim taxonomy) | Brief claims must satisfy SPEC-011 — 0 unsupported claims |
| UHI-SPEC-009 (priority ranking) | Brief decision section uses SPEC-009 ranking |
| UHI-SPEC-010 (intervention rules) | Brief decision section references SPEC-010 intervention categories |
| Evidence log (evidence_log table) | Brief claims trace to evidence log entries |

---

*This specification governs the Urban Heat Brief output. All Brief composition must conform to these rules.*
