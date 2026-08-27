# Urban Heat Intelligence — Video Production Script

**Version:** 1.0.0
**Date:** 2026-08-27
**Duration:** ~3:00
**Format:** 1080p (record at 1440p/4K for crop headroom)
**Owner:** urban-heat-intelligence
**Authority:** S4 authorization — submission production

---

## Production Rules

1. **AI footage illustrates. Real evidence proves.** Product footage must be unmistakably real.
2. **No fabrication.** FortyGuard output, NWS output, Urban Heat Brief, QA evidence, screenshots — all real.
3. **Near-tie honesty.** Never narrate "clear best location" when candidates are near-tied.
4. **FortyGuard centrality.** FortyGuard is the primary platform. All other sources are supplementary or deferred.

---

## Narration Map (Evidence-Locked)

| Line | Evidence Class | Source |
|------|---------------|--------|
| "On an extreme summer afternoon in Phoenix…" | general framing | Stock footage |
| "Where should Phoenix prioritize a cooling intervention?" | product question | Product UI |
| "FortyGuard evaluates hundreds of thermal features" | FortyGuard | Product: 367 features |
| "Three candidate locations show effectively equivalent thermal burden" | product-derived comparison | Product: near-tie |
| "Environmental parameters add conditions people experience" | FortyGuard | Product: env_params |
| "Official weather context from the National Weather Service" | NWS | Product: LIVE NWS |
| "The Urban Heat Brief translates evidence into attributed narrative" | product-derived | Product: Brief |
| "These locations warrant comparable attention on thermal evidence alone" | product-derived decision note | Product: Brief decision |
| "Every claim traces to its source" | provenance | Product: evidence chain |
| "Replay preserves real FortyGuard responses" | FortyGuard | Product: mode toggle |
| "QA-Pilot independently qualified the product" | QA evidence | Qualification receipt |
| "It helps decision-makers understand where to look first" | general framing | Closing |

---

## Script

### 0:00–0:15 — Human Problem

**Visual:** Phoenix aerial → street-level heat → people in sun

**Narration:**
"On an extreme summer afternoon in Phoenix, knowing that the city is hot isn't enough. For planners, the harder question is: where should limited cooling resources be investigated first?"

**Production:** Stock or licensed footage. No product yet.

---

### 0:15–0:35 — Product Question

**Visual:** Transition to UHI application. Map loads. Question visible.

**Narration:**
"That's the question Urban Heat Intelligence answers — powered by FortyGuard thermal intelligence."

**Text overlay:**
```
Urban Heat Intelligence
Powered by FortyGuard
```

**Production:** Real screen recording of application loading.

---

### 0:35–0:55 — FortyGuard Analysis

**Visual:** Heatmap polygons render. 367 features visible on map.

**Narration:**
"The agent begins with FortyGuard — evaluating 367 thermal features across the queried Phoenix area. Each feature carries an observed temperature from FortyGuard's 2-meter resolution thermal mapping."

**Production:** Real product footage. Call out 367 features.

---

### 0:55–1:14 — Candidate Comparison

**Visual:** Top-3 candidate cards appear. Near-tie disclosure visible.

**Narration:**
"Three candidate locations show effectively equivalent thermal burden. Their measured temperatures fall within the 0.1°C near-tie tolerance — so thermal evidence alone does not support a meaningful distinction among them."

**Production:** Real product footage. Show near-tie disclosure text.

---

### 1:14–1:42 — Multi-Source Context

**Visual:** NWS weather context appears (LIVE mode or NWS exclusion in Replay).

**Narration:**
"Official weather context from the National Weather Service adds current conditions when available. In historical Replay, this context is explicitly excluded to preserve provenance integrity."

**Production:** Real product footage. Show NWS section or exclusion message.

---

### 1:42–1:54 — SIGNATURE: Urban Heat Brief

**Visual:** Urban Heat Brief card slides into view.

**Narration:**
"The same evidence becomes a concise, attributable heat brief — something a planner, journalist, or resident could actually use."

**Brief content shown:**
```
URBAN HEAT BRIEF — Historical Replay

THERMAL FINDING
FortyGuard identified the highest measured thermal burden among
367 evaluated heatmap features.

CANDIDATE INTERPRETATION
Three candidate locations show effectively equivalent thermal burden.

WEATHER CONTEXT
Current NWS context is not included in historical Replay.

DECISION NOTE
These locations warrant comparable attention on thermal evidence alone.

Sources: FortyGuard (replay)
```

**Production:** Real product footage. This is the hero moment.

---

### 1:54–2:06 — Decision Interpretation

**Visual:** Brief decision note highlighted.

**Narration:**
"The recommendation isn't a black-box score. It's a bounded interpretation of measured evidence — and when candidates are near-tied, the product says so honestly."

**Production:** Real product footage.

---

### 2:06–2:29 — Why This Answer / Provenance

**Visual:** "Why This Answer?" expands. Evidence chain visible.

**Narration:**
"Every claim traces to its source — what was requested, which provider supplied it, when it was observed, and how it contributed to the answer. Source, observation time, and the steps used to reach the recommendation remain inspectable."

**Production:** Real product footage. Show evidence chain nodes.

---

### 2:29–2:39 — Live vs Replay Integrity

**Visual:** Toggle between REPLAY and LIVE mode.

**Narration:**
"Replay preserves real historical FortyGuard responses for deterministic demonstration. Live uses current provider execution. The two are never silently mixed."

**Production:** Real product footage. Show mode toggle.

---

### 2:39–2:48 — QA-Pilot Qualification

**Visual:** Qualification receipt or summary.

**Narration:**
"The frozen product was independently qualified by QA-Pilot — qualified with known limitations, not claimed as flawless."

**Production:** Brief governance section. ~8-10 seconds.

---

### 2:48–3:00 — Closing

**Visual:** Return to map / Phoenix footage.

**Narration:**
"Urban Heat Intelligence doesn't just show that a city is hot. It helps decision-makers understand where to look first — and gives them the evidence to understand why."

**Production:** Clean closing. Logo/end card.

---

## Evidence Constraints

- All product footage must be real screen recordings from the deployed application
- Brief content must match actual rendered Brief (not fabricated)
- Near-tie language must match actual product disclosure
- NWS behavior must match actual mode-gated implementation
- QA claim must match actual qualification outcome: QUALIFIED_WITH_KNOWN_LIMITATIONS
- No fabricated FortyGuard output, NWS output, or provider data
