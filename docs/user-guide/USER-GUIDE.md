# Urban Heat Intelligence — User Guide

**CANONICAL — Owner accepted 2026-08-27**

---

## What Is Urban Heat Intelligence?

Urban Heat Intelligence (UHI) is a heat decision-support tool. It answers the question: **"Where should a city prioritize cooling intervention?"**

Unlike typical heat dashboards that show temperature numbers, UHI explains how the answer was built. Every assertion carries source attribution, timestamps, and provenance — you can trace any claim back to where it came from.

---

## How to Use the Product

### Default: Replay Mode

When you open the product, you start in **Replay mode** with the **Luna dashboard**. This uses pre-recorded data from FortyGuard's thermal mapping of Phoenix, captured on August 25, 2026. No credentials or setup is required — it works immediately.

Replay mode lets you explore the product's full functionality with genuine data, including:
- Ranked priority locations by measured thermal burden
- Representative environmental context (humidity, apparent temperature, heat index) — shared historical context, not independent per-candidate measurements
- The Urban Heat Brief (a human-readable narrative)
- The evidence chain ("Inspect evidence +" panel)

### Optional: Live Mode

If you have a FortyGuard API key, you can switch to **Live mode** to query current thermal data. Live mode makes real API calls and returns data from the present moment. All responses are clearly labeled "Live data" with a green indicator.

To use Live mode, you need:
- A FortyGuard API key (set as `FORTYGUARD_API_KEY` environment variable or placed in `.secrets/fortyguard.env`)

### Switching Between Modes

The mode toggle (LIVE / REPLAY) is visible in the interface. When you switch:
- All data is re-labeled with the new mode
- The evidence chain updates accordingly
- Live and Replay data are never mixed without explicit disclosure

---

## Interpreting the Urban Heat Brief

The Urban Heat Brief is the product's primary output — a concise, attributed narrative you can share or publish. It contains these sections:

### Thermal Finding
Describes what FortyGuard measured — the highest thermal burden among evaluated features, the leading candidate's temperature, the area mean, and environmental parameters.

### Candidate Interpretation
Explains whether locations are meaningfully distinct or near-tied (within 0.1°C of each other). If candidates are near-tied, the Brief states that thermal evidence alone does not support a meaningful distinction.

### Weather Context
In Live mode, this may include NWS (National Weather Service) context when available. In Replay mode, this section states: "Current NWS context is not included in historical Replay."

### Decision Note
States where investigation should be prioritized based on observed evidence. The product recommends where to investigate — it does not claim to predict intervention effectiveness.

### Sources
Lists every data source that contributed to the Brief, with mode labels.

---

## Reading the Evidence Chain

Every assertion in the product traces to a specific data source. You can view this by clicking **"Inspect evidence +"** in the interface.

The evidence chain shows:
- Which tool produced each data point (e.g., FortyGuard heatmap, env_params)
- The source provider (FortyGuard, NWS)
- The timestamp of the observation
- The mode (Live or Replay)
- The query parameters used

For example:
```
FortyGuard heatmap (Replay, Aug 25 2026 14:00 MST)
  → 367 features analyzed
  → Top feature: 42.05°C at [coordinate]
  → Area mean: 42.03°C

FortyGuard env_params (Replay, Aug 25 2026 14:00 MST)
  → Apparent temperature: 46.4°C
  → Humidity: 11.3%
```

---

## What "Near-Tie" Means

When the top candidates have observed temperatures within **0.1°C** of each other, the product marks them as **near-tied**. This means thermal evidence alone does not meaningfully distinguish between them.

The product is honest about this: it is better to say "thermally equivalent" than to falsely pretend that 42.0525°C meaningfully outranks 42.0521°C. Additional local context would be needed to select one location over another.

---

## Mode Labels

Every piece of data in the product carries a mode label:

| Mode | Label | Color | What It Means |
|------|-------|-------|---------------|
| LIVE | "Live data" | Green | Real-time data from current API calls |
| REPLAY | "Replay data — Aug 25, 2026" | Amber/grey | Pre-recorded genuine FortyGuard data |

The mode label is always visible:
- In the data display
- In the "Why?" evidence panel
- In the Urban Heat Brief
- In any exported report

A mixed-provenance display (combining Live and Replay data) is always explicitly labeled — you will never see unlabeled data.

---

## What the Product Does Not Do

- **Does not select specific interventions.** It recommends where to investigate, not what action to take.
- **Does not produce opaque scores.** Rankings are based on observed temperature, not hidden algorithms.
- **Does not fabricate data.** When a source is unavailable, the product discloses the absence and continues with available data.

---

## Data Sources

| Source | Role | Availability |
|--------|------|-------------|
| FortyGuard | Primary thermal intelligence (required) | Always — product cannot function without it |
| Phoenix GIS | Local context (canopy, parks) | Always — context only, not used for ranking |
| NWS | Supplemental weather context | Live mode only, optional |

FortyGuard is the only required source. Phoenix GIS provides local context (canopy coverage, mapped parks) that does not influence the thermal ranking. The product degrades gracefully when optional sources are unavailable — you will always see an honest disclosure of what is and is not included.

---

*This document is CANONICAL — Owner accepted 2026-08-27.*
