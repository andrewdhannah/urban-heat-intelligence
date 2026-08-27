# Urban Heat Intelligence — Demo Scenario

**Version:** 1.0.0
**Date:** 2026-08-26
**Owner:** urban-heat-intelligence
**Duration:** 3 minutes

---

## Scene 1: Opening (20 seconds)

**Visual:** Phoenix map with heat overlay.

**Narration:**
"Where should Phoenix prioritize a cooling intervention this afternoon?"

**Action:** Type the question into the chat interface.

---

## Scene 2: FortyGuard Analysis (40 seconds)

**Visual:** 367 thermal features load on the map. Heat overlay intensifies.

**Narration:**
"FortyGuard's 2-meter resolution thermal mapping reveals 367 distinct thermal features across the queried Phoenix area."

**Action:** Agent identifies three candidate hotspots. Environmental parameters are retrieved for each.

**Visual:** Three locations highlighted on map with temperature labels.

**Narration:**
"The agent identifies three candidate locations and retrieves detailed environmental parameters for each."

---

## Scene 3: Decision (30 seconds)

**Visual:** Top-3 ranking appears in chat. Priority #1 highlighted.

**Narration:**
"It isn't simply giving us the hottest pixel. It's gathering evidence about candidate locations and explaining why one deserves attention first."

**Action:** Agent displays priority scores and intervention recommendation.

**Visual:** Priority #1: "Shade/Canopy intervention recommended — 12% canopy coverage, high pedestrian exposure."

**Narration:**
"Location A ranks first not because it's the hottest, but because it combines the highest heat burden with the greatest cooling deficit."

---

## Scene 4: Multi-Source Intelligence (35 seconds)

**Visual:** NWS weather context appears in the Brief — LIVE only (or "NWS not included in Replay" in Replay mode).

**Narration:**
"The agent also draws on official weather context when available."

**Action:** Agent shows NWS context in the Urban Heat Brief (LIVE mode only).

**Visual:** Brief displayed as styled card with FourGuard thermal finding, near-tie interpretation, weather context, and decision note.

**Narration:**
"The Urban Heat Brief translates technical analysis into a concise, attributable narrative."

---

## Scene 5: Provenance (30 seconds)

**Visual:** User clicks "Why This Answer?"

**Narration:**
"Every assertion carries its source."

**Action:** Evidence chain expands showing:
- FortyGuard heatmap (Replay, Aug 25 2026 14:00) — 367 features
- FortyGuard env_params (Replay, Aug 25 2026 14:00) — Apparent temp: 46.4°C
- NWS exclusion (Replay) — "Current NWS context not included in historical Replay"
- Brief claim provenance — machine-readable per claim

**Action:** Toggle between LIVE and REPLAY mode.

**Narration:**
"Replay data is clearly labeled and cannot masquerade as live data. Every data point carries its mode, source, and timestamp."

---

## Scene 6: Governance (25 seconds)

**Visual:** Brief view of the evidence chain and QA badge.

**Narration:**
"Every important result retains source, time, and provenance. An independent QA agent verifies the final product — testing analytical correctness, provenance integrity, mode separation, and graceful degradation."

**Visual:** "0 unsupported claims. 6 qualification areas. Full reproducibility."

**Narration:**
"That's Urban Heat Intelligence — evidence-backed heat decision support for the cities that need it most."

---

## Backup Scenarios

### If network is slow

Skip multi-source segment. Focus on FortyGuard analysis + decision + provenance.

### If LIVE mode fails

Switch to REPLAY. Explain: "This is pre-recorded FortyGuard data from August 25th. The product works identically with live data."

### If asked about governance

Brief explanation: "Every assertion carries a receipt. The agent cannot present unattributed data. An independent QA agent verifies the product before submission."

---

## Key Messages

1. **Not a dashboard** — an agent that explains its reasoning
2. **Thermal intelligence** — FortyGuard primary source with NWS corroboration (LIVE only)
3. **Human-readable output** — the Urban Heat Brief with claim-level provenance
4. **Every assertion traceable** — provenance model
5. **Independent verification** — QA-Pilot qualifies the product

Note: Phoenix GIS, NOAA, and local news are deferred and not currently integrated.
