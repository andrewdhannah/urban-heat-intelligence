# Urban Heat Intelligence — Decision Flow Teaching Document

**Document ID:** UHI-DECISION-FLOW-TEACHING-001
**Purpose:** Enable a fresh agent to understand how the product makes decisions.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Decision Overview

The product makes one central decision: **Which location should a city investigate first for cooling intervention?**

The current implementation ranks a small set of candidates by observed
thermal burden. It recommends where to prioritize investigation, not a proven
intervention or intervention outcome. GIS, demographic, NOAA, and news inputs
are not currently integrated.

---

## 2. Current Thermal Ranking

### 2.1 Implemented evidence

| Component | Code | Source | Meaning |
|-----------|------|--------|---------|
| Observed temperature | — | FortyGuard heatmap | Temperature of the evaluated feature |
| Area mean | — | FortyGuard heatmap aggregate | Reference temperature for the query area |
| Environmental parameters | — | FortyGuard env_params | Apparent temperature, heat index, and humidity |

### 2.2 Deferred context dimensions

Phoenix GIS, demographic context, NOAA history, and local reporting are
deferred. They must not be inferred from the current ranked response.

### 2.3 Ranking method

```
Candidates are sorted by `observed_temp` descending. The first three
temperature-bearing candidates are returned. No opaque score is created.
```

Missing environmental parameters cause that candidate's env_params result to
be skipped; no replacement value is fabricated.

### 2.4 Near-tie threshold

Candidates whose observed-temperature spread is below **0.1°C** are marked
`ranking_status: near_tie`. Stable internal ordering remains available for
display, but the Brief states that thermal evidence does not meaningfully
distinguish the candidates.

---

## 3. Candidate Selection

### 3.1 How Candidates Are Identified

1. FortyGuard heatmap returns all thermal features in the query area
2. Agent derives centroid coordinates and sorts temperature-bearing features
3. The top three candidates receive env_params requests
4. Comparative evidence is returned for the decision response

### 3.2 What "Top-3" Means

The top 3 are the three highest observed-temperature candidates returned by
the current FortyGuard heatmap normalization. This is a thermal investigation
ordering, not an intervention-opportunity score.

### 3.3 Near-Tie Handling

When candidate temperatures have a spread below 0.1°C, the agent says so honestly:

**Near-tie case:**
```text
Three locations show effectively equivalent thermal burden in this
observation. FortyGuard identifies them as the highest-burden candidates,
but thermal evidence alone does not support a meaningful distinction
between them. Additional local context would be needed before selecting
one intervention location over another.
```

**Why this matters:** It is better to say "thermally equivalent" than to falsely pretend that 42.0525°C meaningfully outranks 42.0521°C. Intellectual honesty strengthens the product's credibility.

---

## 4. Intervention Boundary

### 4.1 The 6 Intervention Categories

| Category | When Selected | Example Action |
|----------|--------------|----------------|
| Shade/Canopy | Low canopy coverage + high pedestrian exposure | Plant trees, install shade structures |
| Cool Surface | Large impervious surfaces + high thermal mass | Cool pavement, reflective roofing |
| Cooling Center | High population density + limited existing cooling | Open/expand cooling centres |
| Green Infrastructure | Available space + high cooling deficit | Parks, green corridors, bioswales |
| Early Warning | High exposure + variable conditions | Alert systems, outreach programs |
| Policy/Planning | Systemic issues + governance opportunity | Zoning changes, building codes |

### 4.2 How Intervention Is Selected

The current product does not select a specific intervention category. It
answers where to prioritize investigation based on measured thermal evidence.
Specific intervention logic requires the deferred GIS, demographic, and
policy context and is outside the frozen implementation.

### 4.3 Intervention Never Fabricates

The agent does not claim that any intervention will be effective or that a
particular location has a proven policy outcome.

---

## 5. Multi-Source Decision Enrichment

### 5.1 Source Contributions to Decision

| Source | Decision Contribution |
|--------|----------------------|
| FortyGuard | Observed thermal measurements, candidate ranking, environmental parameters |
| NWS | LIVE-only supplemental weather context; never ranking input |
| Phoenix GIS | Deferred, not integrated |
| NOAA | Deferred, not integrated |
| Local news | Not authorized, not integrated |

### 5.2 Source Absence Handling

| Scenario | Decision Impact |
|----------|----------------|
| FortyGuard unavailable | Decision cannot be made. Error state. |
| NWS unavailable | Thermal decision continues; Brief discloses NWS unavailability in LIVE or excludes it in Replay. |
| GIS unavailable | No GIS claim is generated. |
| NOAA unavailable | No historical comparison is generated. |
| News unavailable | No human-interest claim is generated. |

---

## 6. Decision Output Structure

The agent produces an analytical view and an Urban Heat Brief in the browser
payload for a successful heatmap result:

### 6.1 Analytical View

```text
Top 3 Priority Locations:

1. [Location A] — Priority Score: 0.87
   Heat Burden: TS=0.9, HP=0.8, EF=0.7, DS=0.6
   Intervention: Shade/Canopy (canopy deficit: 12%, pedestrian exposure: high)
   Confidence: 82%

2. [Location B] — Priority Score: 0.79
   ...

3. [Location C] — Priority Score: 0.71
   ...

Why this answer?
[Expandable evidence chain with source attribution for each component]
```

### 6.2 Urban Heat Brief

```text
Urban Heat Brief — Historical Replay — 2026-08-25T14:00:00-07:00

THERMAL FINDING
FortyGuard identified the highest measured thermal burden among 367 evaluated
heatmap features. The leading candidate near [coordinate] measured approximately
[observed temperature]°C against an area mean of [area mean]°C. FortyGuard
environmental parameters at that candidate report an apparent temperature of
[apparent temperature]°C.

CANDIDATE INTERPRETATION
Three candidate locations show effectively equivalent thermal burden in this
observation. Their measured temperatures fall within the 0.1°C near-tie tolerance,
so thermal evidence alone does not support a meaningful distinction among them.
Additional local context would be needed before selecting one location.

WEATHER CONTEXT
Current NWS context is not included in historical Replay.

DECISION NOTE
These locations warrant comparable attention on thermal evidence alone.

Sources: FortyGuard (replay)
```

The displayed Brief uses actual runtime values, not the placeholders above. A
clear ranking uses bounded measured differences; a near-tie never presents the
stable internal ordering as meaningful policy superiority. In Replay, current
NWS context is explicitly excluded. In LIVE, NWS may appear as supplemental
context with its own retrieval time and `used_in_decision: false` metadata.

---

## 7. Provenance Rules for Decisions

Every component of the decision must carry provenance:

| Decision Component | Required Provenance |
|-------------------|---------------------|
| Temperature reading | Source, tool, timestamp, mode |
| Priority score | All component values and their sources |
| Intervention selection | SPEC-010 rule that triggered selection |
| Confidence level | List of missing data sources that reduced confidence |
| Historical comparison | NOAA source, comparison period, deviation value |

**The decision is not valid without its provenance.** If provenance cannot be established, the decision must not be presented.

---

*This document explains the decision logic to a fresh agent. It implements UHI-SPEC-009 and UHI-SPEC-010.*
