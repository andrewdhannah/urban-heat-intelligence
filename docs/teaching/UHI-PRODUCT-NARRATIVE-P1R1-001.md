# Urban Heat Intelligence — Stabilized Product Narrative & Evidence-Role Rules

**Document ID:** UHI-PRODUCT-NARRATIVE-P1R1-001
**Purpose:** Record the stabilized product thesis, evidence roles, temporal rules, and pre-freeze Shape so later agents do not reconstruct them from conversation.
**Status:** CANONICAL (P1-R1 pre-freeze)
**Owner:** urban-heat-intelligence
**Base:** P1 candidate `bb6e1cc` (refinement/dash-v2-p1-map-legibility)
**Supersedes:** none (additive to UHI-PRODUCT-TEACHING-001)

---

## 1. Product Thesis (Canonical)

> **Citywide heat requires local decisions.**
>
> Urban Heat Intelligence uses FortyGuard as the measured spatial evidence that localizes thermal burden, then combines authoritative contextual sources to help people understand the location, the conditions around it, and the available response options — **without allowing contextual evidence to alter the thermal ranking.**

## 2. Design Rule (Canonical)

Every capability must do at least one of:

1. **localize the heat** — identify where measured thermal burden concentrates;
2. **explain a localized result** — describe the location and its surroundings;
3. **connect the localized result to a useful response** — point to available human-response resources;
4. **explain why the result can be trusted** — provenance and source roles.

If a capability advances none of these four purposes, it does not belong in the pre-freeze product.

## 3. Evidence Roles (Canonical)

| Source | Role | Ranking Effect |
|--------|------|----------------|
| **FortyGuard** | Primary measured thermal decision evidence | **Determines** thermal candidate ranking |
| **Phoenix GIS** | Local physical context (canopy, parks) | Never changes thermal ranking |
| **NWS** | Atmospheric observation / forecast / alert context | Never changes thermal ranking |
| **Local reporting** | Bounded civic context | Never changes thermal ranking |
| **Heat Relief Network** | Human-response / resource context | Never changes thermal ranking |
| **Urban Heat Brief / Analyst** | Derived explanation of governed evidence | Never invents unsupported evidence |

**Core framing:**
- NWS / reporting explain broader city conditions.
- FortyGuard localizes where measured thermal burden concentrates.
- Phoenix GIS explains the candidate surroundings.
- Heat Relief Network connects candidate locations to available human-response resources.
- **Context never changes thermal ranking.**

## 4. Temporal Rules (Canonical)

### 4.1 Replay vs. Live

- **Replay** is a reproducible historical capture (Aug 25, 2026 14:00 MST). It must be deterministic and require zero network calls for the thermal core.
- **Live** is genuine current provider data. Live must never silently fall back to Replay.
- Live and Replay data must never contaminate each other.

### 4.2 Contemporaneous vs. Same-Day Retrospective

For any captured historical context (NWS observation, alerts, local reporting):

- **CONTEMPORANEOUS WITH REPLAY:** Published/issued at or before the Replay observation time (Aug 25, 14:00 MST). This is information that could have been available to a decision-maker at capture time.
- **SAME-DAY RETROSPECTIVE:** Published or updated after the captured observation (e.g., a 9:58 PM article about a 2:00 PM event). This must be labeled as same-day retrospective, never implied to have been available at capture time.

Preserve publication metadata (published_at, updated_at where available, retrieved_at) and the temporal relationship to Replay.

### 4.3 NWS Observation vs. Forecast

- A **station observation** is a measured value at a specific station and time.
- A **forecast-period value** is a predicted value for a future period.
- The current NWS helper consumes forecast-period data. It MUST NOT be labeled as a station observation.
- Current NWS forecast data must NEVER be projected backward into historical Replay.

### 4.4 NWS Station Air Temperature ≠ FortyGuard Thermal-Cell Temperature

An NWS station air temperature is a point measurement of air temperature. A FortyGuard thermal-cell value is a measured surface/thermal value for a spatial cell. They are different measurements and must never be presented as equivalent.

## 5. Pre-Freeze Target Shape (P1-R1)

The pre-freeze target Shape is **P1-R1**, a bounded refinement layered on the P1 candidate (`bb6e1cc`). It is NOT a clean-sheet redesign.

```
P1 CANDIDATE (bb6e1cc)  [base — known-good, not frozen]
        ↓
P1-R1 PRE-FREEZE TARGET SHAPE
    ├── CORE HARDENING (required)
    │     A1 Candidate overlap z-index elevation
    │     A2 FortyGuard measured-area clarity + geo-registration proof
    │     A3 Responsive / result-density hardening
    │     A4 Live latency UX
    │     A5 Global °C / °F units
    │     A6 Live NWS truthfulness
    │     A7 Guided analyst / question catalogue
    │     A8 FortyGuard connection in analyst answers
    │
    ├── CONTEXTUAL CAPABILITIES (independently gated, droppable)
    │     B1 Historical NWS for Replay
    │     B2 Heat Relief Network
    │     B3 Historical alerts
    │     B4 Bounded local reporting
    │
    └── DOCUMENTATION
          This narrative + evidence-role rules
```

### 5.1 Capability Priority / Drop Order (Stage B)

Preserve in this order:
1. historical NWS temporal coherence (B1)
2. Heat Relief human-response capability (B2)
3. historical alerts (B3)
4. local reporting/news (B4)

If schedule or evidence quality requires scope reduction, drop in the **reverse** order:
local reporting first → alerts → Heat Relief if necessary → historical NWS last.

A dropped capability must:
- be explicitly reported;
- not leave dead UI;
- not appear in demo claims;
- not invalidate the thermal core.

## 6. Thermal Invariants (Preserved)

- FortyGuard is primary decision evidence; it determines ranking.
- Replay 367 cells preserved.
- Near-tie semantics (0.1°C threshold) preserved.
- Live never silently falls back to Replay.
- Phoenix GIS is context-only (`used_in_decision = false`).
- All contextual sources are `used_in_decision = false`.
- 0 unsupported claims maintained.

---

*This document is canonical for the P1-R1 pre-freeze Shape. It is additive to UHI-PRODUCT-TEACHING-001 and does not rewrite earned historical content.*
