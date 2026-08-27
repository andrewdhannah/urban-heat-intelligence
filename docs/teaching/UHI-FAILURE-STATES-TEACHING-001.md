# Urban Heat Intelligence — Failure States Teaching Document

**Document ID:** UHI-FAILURE-STATES-TEACHING-001
**Purpose:** Enable a fresh agent to understand every failure mode and the product's required behavior.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Failure Handling Principle

> **The product must never manufacture plausible-looking evidence to hide dependency failure.**

This is the foundational failure invariant. When a source is unavailable, the product must:
1. Omit the missing source's contribution
2. Disclose the absence
3. Continue with available sources (if FortyGuard is available)
4. Never invent data to fill the gap

---

## 2. Failure Modes by Source

### 2.1 FortyGuard Unavailable

| Property | Value |
|----------|-------|
| **Severity** | CRITICAL |
| **Impact** | Product cannot function |
| **Behavior** | Error state — cannot generate analysis or decision |
| **Display** | "FortyGuard data is currently unavailable. Please try again later." |
| **Brief** | Not generated |
| **Decision** | Not generated |

**Why critical:** FortyGuard is the primary source. Without it, no thermal intelligence exists.

### 2.2 NWS Unavailable

| Property | Value |
|----------|-------|
| **Severity** | NON-CRITICAL |
| **Impact** | Weather context missing |
| **Behavior** | Thermal Brief continues; NWS context is disclosed as unavailable |
| **Display** | "NWS context was unavailable for this LIVE query; it is not used in the thermal decision." |
| **Brief** | Continues with a bounded NWS-unavailable disclosure |
| **Decision** | Exposure factor scored without NWS corroboration |

**Why non-critical:** NWS enriches context but is not required for the core decision.

### 2.3 Phoenix GIS Unavailable

| Property | Value |
|----------|-------|
| **Severity** | NON-CRITICAL |
| **Impact** | Physical context missing |
| **Behavior** | GIS section omitted from brief |
| **Display** | "City GIS data is not currently available." |
| **Decision** | Intervention opportunity scored with reduced data |
| **Brief** | Continues without GIS section |

**Why non-critical:** GIS enriches intervention logic but is not required for ranking.

### 2.4 NOAA Unavailable

| Property | Value |
|----------|-------|
| **Severity** | NON-CRITICAL |
| **Impact** | Historical comparison missing |
| **Behavior** | NOAA section omitted from brief |
| **Display** | "NOAA historical data is not currently available." |
| **Decision** | Deviation score not calculated |
| **Brief** | Continues without historical comparison |

**Why non-critical:** NOAA adds historical context but is not required for current assessment.

### 2.5 Local News Unavailable

| Property | Value |
|----------|-------|
| **Severity** | LOW |
| **Impact** | Human-interest context missing |
| **Behavior** | News section omitted from brief |
| **Display** | [No explicit disclosure needed — section simply absent] |
| **Decision** | No impact |
| **Brief** | Continues without human-interest context |

**Why low:** News is contextual only — never measurement, never decision-critical.

---

## 3. Partial Multi-Source Availability

### 3.1 Scenario Matrix

| FortyGuard | NWS | GIS | NOAA | News | Product Behavior |
|-----------|-----|-----|------|------|-----------------|
| ✓ | ✓ | ✓ | ✓ | ✓ | Full product |
| ✓ | ✓ | ✓ | ✓ | ✗ | Full brief, no human-interest |
| ✓ | ✓ | ✓ | ✗ | - | Brief without historical comparison |
| ✓ | ✓ | ✗ | - | - | Brief without physical context |
| ✓ | ✗ | - | - | - | Minimum enriched brief |
| ✓ | ✗ | ✗ | ✗ | ✗ | Minimum brief (FortyGuard only) |
| ✗ | * | * | * | * | Error state — cannot function |

### 3.2 Graceful Degradation

The product degrades gracefully from full to minimum:

```
Full product (all sources)
    ↓ NWS unavailable
Enriched product (FortyGuard + GIS + NOAA)
    ↓ GIS unavailable
Contextual product (FortyGuard + NOAA)
    ↓ NOAA unavailable
Core product (FortyGuard only)
    ↓ FortyGuard unavailable
Error state
```

At every level, the product is still useful. The minimum brief (FortyGuard only) provides thermal intelligence with attribution.

---

## 4. Data Quality Failures

### 4.1 Stale Data

| Property | Value |
|----------|-------|
| **Detection** | Timestamp comparison with current time |
| **Threshold** | Data older than 1 hour is flagged |
| **Behavior** | Disclose age in display and brief |
| **Display** | "FortyGuard data from 2:15 PM (45 minutes old)" |

### 4.2 Conflicting Sources

| Property | Value |
|----------|-------|
| **Detection** | NWS timestamp differs materially from FortyGuard (>30 min) |
| **Behavior** | Disclose disagreement rather than silently reconcile |
| **Display** | "NWS reports 43.8°C while FortyGuard observes 44.2°C" |
| **Decision** | Use FortyGuard as primary (it is the required source) |

### 4.3 Malformed Response

| Property | Value |
|----------|-------|
| **Detection** | JSON parsing failure, missing required fields |
| **Behavior** | Treat source as unavailable |
| **Display** | "[Source] returned an unexpected response." |
| **Decision** | Continue with remaining sources |

### 4.4 Rate Limited

| Property | Value |
|----------|-------|
| **Detection** | 429 response from API |
| **Behavior** | Retry with backoff (max 2 retries) |
| **If retries exhausted** | Treat as unavailable |
| **Display** | "[Source] rate limit exceeded. Using cached data if available." |

---

## 5. System Failures

### 5.1 Database Unavailable

| Property | Value |
|----------|-------|
| **Severity** | CRITICAL |
| **Impact** | Cannot store evidence, cannot retrieve cache |
| **Behavior** | In-memory fallback for current session only |
| **Limitation** | No persistence, no "Why?" panel for prior queries |

### 5.2 Interface Unavailable

| Property | Value |
|----------|-------|
| **Severity** | CRITICAL |
| **Impact** | User cannot interact |
| **Behavior** | Server returns error page |
| **Recovery** | Restart server |

### 5.3 Network Unavailable

| Property | Value |
|----------|-------|
| **Severity** | CRITICAL (for LIVE mode) |
| **Impact** | Cannot reach FortyGuard API |
| **Behavior** | REPLAY mode available, LIVE mode unavailable |
| **Display** | "Network unavailable. REPLAY mode only." |

---

## 6. What Must Never Happen

| Forbidden Behavior | Why |
|-------------------|-----|
| Inventing temperature data when FortyGuard unavailable | Violates foundational invariant |
| Inventing weather conditions when NWS unavailable | Fabricating evidence |
| Inventing historical comparison when NOAA unavailable | Fabricating evidence |
| Inventing vegetation/park data when GIS unavailable | Fabricating evidence |
| Omitting failure disclosure | User cannot assess data completeness |
| Mixing Live and Replay without disclosure | Provenance violation |
| Presenting stale data as current | Temporal dishonesty |
| Silently reconciling conflicting sources | Hides disagreement from user |
| Falling back to news for temperature measurement | News is contextual, never measurement |

---

## 7. QA Implication: Negative Tests

The multi-source expansion creates excellent negative tests for QA-Pilot:

| Test | Source State | Expected Result |
|------|-------------|----------------|
| FortyGuard + NWS partial failure | FortyGuard OK, NWS fails | Decision works, NWS shown unavailable |
| FortyGuard + GIS partial failure | FortyGuard OK, GIS fails | No invented vegetation conclusion |
| NWS timestamp conflict | NWS and FortyGuard timestamps differ >30min | Timestamps remain distinct |
| NOAA unavailable | FortyGuard + NWS + GIS OK | No historical comparison generated |
| News unavailable | All others OK | No fabricated human-interest context |
| Mixed provenance | Replay FortyGuard + Live NWS | Only if explicitly represented as mixed |
| Stale source | Data >1 hour old | Visibly disclose age |
| Conflicting sources | NWS and FortyGuard disagree | Disclose disagreement, don't reconcile |

These are exactly the kinds of tests that demonstrate why The Librarian / QA-Pilot architecture matters.

---

## 8. Relationship to Other Teaching Documents

| Document | Relationship |
|----------|-------------|
| UHI-PRODUCT-TEACHING-001 | Failure handling is referenced in product constraints |
| UHI-DATA-SOURCES-TEACHING-001 | Source-specific failure modes extend the source catalog |
| UHI-EVIDENCE-PROVENANCE-TEACHING-001 | Failure disclosure is part of provenance |
| UHI-LIVE-REPLAY-TEACHING-001 | Mode integrity during failures |
| UHI-QA-STRATEGY-001 | These failure modes define QA negative test scenarios |

---

*This document explains every failure mode to a fresh agent. It implements the foundational invariant: never manufacture evidence to hide dependency failure.*
