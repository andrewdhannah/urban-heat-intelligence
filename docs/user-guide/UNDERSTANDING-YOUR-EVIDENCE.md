# Urban Heat Intelligence — Understanding Your Evidence

**CANDIDATE — not canonical until Owner acceptance**

---

## What Is an Evidence Chain Node?

Every time the product retrieves data, it appends an **evidence chain node** — a record that traces exactly where each data point came from. This is not optional; it is an architectural requirement. An assertion without provenance is treated as a bug.

An evidence node looks like this:

```json
{
  "step": "heatmap_result",
  "data": { "tool": "get_heatmap", "feature_count": 367, "mode": "replay" },
  "timestamp": "2026-08-26T14:15:00+00:00"
}
```

Every evidence node contains:
- **step** — which pipeline stage produced this (heatmap_result, env_params_result, etc.)
- **data** — payload specific to that stage
- **timestamp** — when the node was created

The evidence chain is stored in-memory and serialized into the JSON API response. It is not persisted to a database.

In Replay mode, the chain includes an `nws_exclusion` node showing that current NWS context is not included.

---

## The Claim Taxonomy (10 Classes)

Every assertion the product makes belongs to one of 10 normative claim classes defined in UHI-SPEC-011. This taxonomy is machine-verifiable:

| # | Normative Class (SPEC-011) | Product Alias in Brief | Example |
|---|---------------------------|----------------------|---------|
| 1 | SOURCE_OBSERVATION | thermal measurement | "FortyGuard observed 42.05°C" |
| 2 | NORMALIZED_OBSERVATION | — (mechanical) | Source observation normalized to evidence schema |
| 3 | DERIVED_FINDING | product_derived_comparison | "3 candidates within 0.1°C near-tie tolerance" |
| 4 | CORROBORATED_FINDING | — (not currently produced) | Finding supported by 2+ independent sources |
| 5 | HISTORICAL_COMPARISON | — (NOAA deferred) | "2°C above 30-year average" |
| 6 | PRIORITY_CLASSIFICATION | product_derived_decision_note | "These locations warrant comparable attention" |
| 7 | INTERVENTION_RECOMMENDATION | — (deferred) | Recommended action based on analysis |
| 8 | CONTEXTUAL_STATEMENT | official_current_context, provenance_disclosure | "NWS reports Partly Cloudy conditions" |
| 9 | UNRESOLVED | — (not currently produced) | Identified but unanswered question |
| 10 | UNSUPPORTED | [forbidden] | [must not appear] |

The product must maintain **0 unsupported claims** at all times. This is machine-verifiable.

---

## What "0 Unsupported Claims" Means

Every statement the product makes must belong to one of the 9 active claim classes above. The "UNSUPPORTED" class is forbidden — no assertion may appear without traceable provenance.

When you see the evidence chain, every line traces to a specific evidence chain node. There are no orphan claims, no invented data, and no unattributed assertions. If a source is unavailable, the product discloses the absence rather than fabricating a substitute.

---

## Source Hierarchy

### Primary: FortyGuard

FortyGuard is the only **required** source. The product cannot function without it. FortyGuard provides:
- 2m-resolution thermal mapping
- Temperature measurements and hotspot rankings
- Environmental parameters (humidity, wind, apparent temperature)
- Heat index calculations

Every thermal assertion in the product traces to FortyGuard data.

### Supplemental: NWS (National Weather Service)

NWS is **optional** and available only in Live mode. It provides:
- Current weather conditions (independent of FortyGuard)
- Active heat advisories and warnings
- Short-term forecasts

NWS data is always marked as **supplemental** and **`used_in_decision: false`**. It enriches context but never influences the thermal ranking.

### Deferred Sources

Phoenix GIS, NOAA, and local news are **not currently integrated**. The product does not consult these sources. If you see them mentioned in documentation, they represent future capabilities, not current functionality.

---

## Live vs. Replay Labels

Every piece of data in the product carries a mode label:

| Mode | Label | What It Means |
|------|-------|---------------|
| LIVE | "Live data" — green | Real-time data from current API calls |
| REPLAY | "Replay data — Aug 25, 2026" — amber/grey | Pre-recorded genuine FortyGuard data |

The mode label appears:
- In every data display
- In the "Why?" evidence panel
- In the Urban Heat Brief
- In any exported report

**Provenance integrity rule:** Live and Replay data are never mixed without explicit labeling. A Replay data point is never presented as Live, and vice versa.

---

## What the "Why?" Panel Shows

When you click **"Why This Answer?"**, the product displays the complete evidence chain for every assertion. This panel shows:

1. **Which data sources contributed** — e.g., FortyGuard heatmap, FortyGuard env_params
2. **The timestamp of each observation** — when the data was captured
3. **The mode of each source** — Live or Replay, with date
4. **The specific values returned** — temperatures, humidity, feature counts
5. **How candidates were compared** — the ranking method and near-tie threshold
6. **What sources were excluded** — and why (e.g., "NWS excluded in Replay")

Every line in the "Why?" panel traces to a specific evidence chain node. There is no fabricated evidence in the chain.

---

## Near-Tie Semantics

When the top candidate locations have observed temperatures within **0.1°C** of each other, they are marked as **near-tied** (`ranking_status: near_tie`).

What this means:
- The product presents them in a stable internal order for display purposes
- But the Brief states that thermal evidence alone does not meaningfully distinguish between them
- Additional local context would be needed before selecting one location over another

What this does NOT mean:
- That one location is "better" than another
- That the ranking order implies policy superiority
- That you should ignore the tie and pick one anyway

The product is transparent about uncertainty. Intellectual honesty strengthens credibility.

---

## How Provenance Works in the Urban Heat Brief

The Urban Heat Brief — the product's narrative output — inherits the same provenance model. Every sentence traces to evidence:

| Brief Sentence | Evidence Trace |
|----------------|---------------|
| "FortyGuard identified the highest measured thermal burden among 367 evaluated heatmap features" | FortyGuard heatmap result |
| "The leading candidate measured approximately 42.05°C against an area mean of 42.03°C" | FortyGuard heatmap + coordinate selection |
| "FortyGuard environmental parameters report an apparent temperature of 46.40°C" | FortyGuard env_params result |
| "3 candidate locations show effectively equivalent thermal burden" | Product-derived comparison (0.1°C threshold) |
| "Current NWS context is not included in historical Replay" | Provenance disclosure |

The narrative may simplify evidence for readability. It may never invent or blur evidence.

### Brief Claim Provenance

Each Brief claim carries structured metadata in a machine-readable envelope:

| Field | Meaning |
|-------|---------|
| `claim_id` | Unique identifier for this claim |
| `text` | The narrative sentence |
| `source_provider` | Which data provider (FortyGuard, UHI) |
| `source_type` | Product alias mapping to SPEC-011 normative class |
| `evidence_nodes` | References to specific evidence chain nodes |
| `mode` | Live or Replay |
| `observation_time` | When the observation was captured |
| `used_in_decision` | Whether this claim influenced the ranking |
| `governing_threshold_celsius` | Near-tie threshold (0.1°C) when applicable |

This envelope is distinct from the runtime evidence chain. The evidence chain records what happened during execution. The claim envelope records what the Brief asserts and why.

---

## What Must Never Happen

- The product must never fabricate temperature data when FortyGuard is unavailable
- The product must never invent weather conditions when NWS is unavailable
- The product must never present Replay data as Live
- The product must never omit the mode label from any displayed data
- The product must never silently reconcile conflicting sources — it discloses disagreements
- The product must never use news articles as temperature sources

---

*This document is CANDIDATE — not canonical until Owner acceptance.*
