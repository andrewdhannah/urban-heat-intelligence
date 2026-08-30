# Pitch — Urban Heat Intelligence

## One-Liner

> Turns FortyGuard heat data into ranked, explainable intervention priorities so cities know where to act first — and why.

## The Problem

Phoenix experiences some of the most extreme urban heat in the United States. FortyGuard measures it at 2m resolution — the height where people actually feel it. But raw temperature data doesn't answer the question cities need answered: **"Where do we intervene first, and why?"**

Dashboards show numbers. Heatmaps show color gradients. Neither tells a city planner which block to prioritize, how the top candidates compare, or what evidence supports the decision.

## The Solution

Urban Heat Intelligence takes FortyGuard's measured thermal field and turns it into **ranked, explainable intervention priorities** with full provenance.

Every answer shows its work:
- Which FortyGuard cells were evaluated
- How the top-3 candidates were selected
- What the environmental conditions are at each location
- Whether the candidates are genuinely different or effectively tied
- What corroborating weather context exists

This is decision support with visible receipts — not a black box.

## How It Works

```
FortyGuard Heatmap (367 cells) → Candidate Extraction → Top-3 Ranking
    → Environmental Parameters → NWS Corroboration → Urban Heat Brief
    → Evidence Chain (provenance for every claim)
```

1. **FortyGuard Heatmap** — 2m-resolution temperature measurement across the area of interest
2. **Candidate Extraction** — Hotspot identification from the measured thermal field
3. **Deterministic Top-3 Ranking** — Ranked by observed temperature; near-tie within 0.1°C flagged
4. **Environmental Parameters** — Heat index, apparent temperature, humidity at each candidate
5. **NWS Corroboration** — Current forecast and alerts (supplemental, never ranks)
6. **Urban Heat Brief** — Derived interpretation with claim-level provenance
7. **Evidence Chain** — Every step recorded with source, mode, and timestamp

## What Makes This Different

**Every other entry shows data. This one explains the decision.**

- **Evidence receipts** — Every answer carries a structured record of which tools were called, what data was returned, and why the system concluded what it concluded
- **Near-tie honesty** — When candidates are within 0.1°C, the system says so instead of fabricating a ranking
- **FortyGuard as central platform** — The thermal measurement is the single source of truth; everything else is context
- **Two modes** — Replay (genuine fixtures, zero network) proves the pipeline works; Live (genuine API calls) proves it works with real data

## Live Demo

- **URL:** https://urban-heat-intelligence.onrender.com/
- **Video:** https://youtu.be/xYDIttapi_o
- **Repo:** https://github.com/andrewdhannah/urban-heat-intelligence

## Submission Tracks

| Track | Designation |
|-------|-------------|
| **Primary** | Track 7 — Data Analysis & Correlation |
| **Secondary** | Track 1 — Resilient Cities & Infrastructure |
| **Secondary** | Track 6 — Agentic AI |

## Team

Solo entry. Built in two weeks on FortyGuard's Temperature API.
