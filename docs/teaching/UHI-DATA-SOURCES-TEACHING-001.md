# Urban Heat Intelligence — Data Sources Teaching Document

**Document ID:** UHI-DATA-SOURCES-TEACHING-001
**Purpose:** Enable a fresh agent to understand every data source, its role, and how it contributes to the product.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Source Hierarchy

The current product is implemented around FortyGuard thermal evidence with
Phoenix GIS local context and optional LIVE NWS corroboration.

```
FortyGuard (PRIMARY — required)
       ↓
Phoenix GIS (LOCAL CONTEXT — always available, used_in_decision=false)
       ↓
NWS (CURRENT CONTEXT — LIVE-only optional)
       ↓
Urban Heat Brief composition
```

---

## 2. Source Details

### 2.1 FortyGuard

| Property | Value |
|----------|-------|
| **Role** | Primary thermal intelligence and hotspot detection |
| **Status** | REQUIRED — product cannot function without it |
| **API Endpoints** | /v1/heatmap, /v1/env_params, /v1/system/fetch-api-key-usage |
| **Premium Endpoints** | /v1/satellite, /v1/streetview, /v1/heat_intelligence |
| **Resolution** | 2m thermal mapping |
| **Data Volume** | 52B data points/day globally, 367+ features per Phoenix query |
| **Auth** | FORTYGUARD_API_KEY (environment variable or .secrets/fortyguard.env) |
| **Pattern** | Async: POST → activity_id → poll GET |
| **Narrative Role** | Temperature measurements, heat burden rankings, hotspot identification |

**What FortyGuard provides:**
- Thermal feature locations and temperatures
- Environmental parameters (humidity, wind, apparent temperature)
- Heat index calculations
- API credit usage

### 2.2 NWS (National Weather Service)

| Property | Value |
|----------|-------|
| **Role** | Current weather and advisory corroboration |
| **Status** | OPTIONAL, LIVE only — enriches context, not required for core decision |
| **API** | api.weather.gov (public, no key required) |
| **Data** | Current conditions, alerts/warnings, forecasts |
| **Narrative Role** | Official weather conditions, advisories, warnings |

**What NWS provides:**
- Current temperature/humidity/wind (independent of FortyGuard)
- Active heat advisories and warnings
- Short-term forecast
- Administrative area context

**Why NWS matters:**
- Official government data adds credibility
- Advisories provide contextual corroboration
- NWS values remain separate from FortyGuard measurements and ranking

**Replay rule:** Replay does not request NWS. The Urban Heat Brief states
that current NWS context is not included in historical Replay.

### 2.3 Phoenix/Maricopa GIS

| Property | Value |
|----------|-------|
| **Role** | Local physical and cooling context |
| **Status** | INTEGRATED — context only, not used for ranking |
| **Data** | Tree canopy coverage, mapped park locations |
| **Narrative Role** | Physical context for candidate locations |

**What GIS provides:**
- Park locations and names
- Canopy coverage percentage at candidate locations
- Census tract identification

**Why GIS matters:**
- Helps explain how candidate environments differ
- Provides local situational awareness after thermal candidates are identified

**Ranking rule:** GIS context is never used for thermal ranking. It is
always marked `used_in_decision: false`.

### 2.4 NOAA

| Property | Value |
|----------|-------|
| **Role** | Historical and climatological context |
| **Status** | DEFERRED — not integrated in the current product |
| **API** | NOAA Climate Data Online (CDO) |
| **Data** | Historical temperature records, climate normals, trends |
| **Narrative Role** | Historical comparison, trend context |

**What NOAA provides:**
- 30-year climate normals for the area
- Historical temperature records
- Trend analysis (is this hotter than usual for this date?)
- Deviation from normal calculation

**Why NOAA matters:**
- Contextualizes current readings ("2°C above 30-year average")
- Supports deviation score in priority model
- Adds scientific credibility

### 2.5 Local News

| Property | Value |
|----------|-------|
| **Role** | Human-interest and community context |
| **Status** | NOT AUTHORIZED — not integrated in the current product |
| **API** | News search (if available) |
| **Data** | Community impact stories, cooling centre activity, human context |
| **Narrative Role** | Human-interest enrichment in Heat Brief |

**What Local News provides:**
- Cooling centre openings and locations
- City heat-response activity
- School/outdoor-program changes
- Public-health messaging
- Power demand issues
- Local impacts of the heat event

**Critical rule:** News never participates in the mathematical ranking. News explains human consequence; authoritative data establishes measurements.

**Correct pattern:** "Local reporting describes heat-related cooling-centre activity near downtown."

**Forbidden pattern:** "The temperature is 44.2°C" (sourced from a news article).

**The distinction:** News provides context about what the heat means for people. FortyGuard and NWS provide measurements and official context. GIS provides local context (canopy, parks) that does not influence ranking. NOAA and local news are not integrated.

---

## 3. Source Interaction Patterns

### 3.1 FortyGuard as Primary Source

The product is anchored by FortyGuard thermal measurements.

```
FortyGuard heatmap: 367 features, top at 42.05°C, area mean 42.03°C
FortyGuard env_params: apparent temperature 46.4°C, humidity 11.3%
→ Urban Heat Brief composes these into attributed narrative
```

### 3.2 Phoenix GIS Context Enrichment

After thermal candidates are identified, Phoenix GIS provides local context for each candidate.

```
Candidate 1: 42.05°C (ranked by FortyGuard)
  GIS: Canopy 0.9%, Inside Roosevelt Park
  → Context only, used_in_decision=false

Candidate 2: 42.05°C (ranked by FortyGuard)
  GIS: Canopy 2.6%, No mapped park
  → Context only, used_in_decision=false
```

GIS context helps explain how candidate environments differ. It does not alter the thermal ranking.

### 3.3 Live NWS Enrichment (LIVE only)

When FortyGuard succeeds in LIVE mode, NWS may add official weather context.

```
FortyGuard: 42.05°C (thermal intelligence, LIVE)
NWS: Partly Cloudy, Extreme Heat Warning active (LIVE context)
→ Brief includes NWS as supplemental context, not ranking input
```

### 3.4 Replay Exclusion

In Replay, no current NWS data is fetched.

```
FortyGuard: 42.05°C (genuine Aug 25 fixture, Replay)
NWS: "Current NWS context is not included in historical Replay."
→ Brief explicitly states NWS exclusion
```
No invented weather conditions. No invented measurements.

---

## 4. Fixture vs Live Data

| Property | Live | Replay (Fixture) |
|----------|------|------------------|
| Source | Real API call | Pre-recorded response |
| Date | Current query time | Aug 25, 2026 |
| Credentials | Required | Not required |
| Label | "Live data" | "Replay data — Aug 25, 2026" |
| Use | Real analysis | Demo, testing, offline |

**Architectural rule:** Live and Replay data must never contaminate each other.

---

## 5. QA Implications

### 5.1 Source Availability Tests

| Test | Expected Result |
|------|----------------|
| All sources available | Full brief generated |
| FortyGuard only | Minimum brief (FortyGuard section + decision only) |
| FortyGuard + NWS only | Brief with weather context, no GIS/NOAA sections |
| FortyGuard unavailable | Error state — cannot generate brief or decision |
| NWS timestamp differs from FortyGuard | Timestamps remain distinct, not reconciled |

### 5.2 Source Hierarchy Tests

| Test | Expected Result |
|------|----------------|
| FortyGuard always present in brief | PASS |
| NWS never used for temperature measurement | PASS |
| GIS never used for weather claims | PASS |
| NOAA never used for current conditions | PASS |
| Local news never used for measurements | PASS |

### 5.3 Negative Tests (Multi-Source Failure)

| Test | Expected Result |
|------|----------------|
| FortyGuard succeeds / NWS fails | Decision works, NWS shown unavailable |
| FortyGuard succeeds / GIS fails | No invented vegetation conclusion |
| NWS timestamp differs materially from FortyGuard | Timestamps remain distinct |
| NOAA unavailable | No historical comparison generated |
| News search unavailable | No fabricated human-interest context |
| Stale source | Visibly disclose age |
| Conflicting sources | Disclose disagreement rather than silently reconcile |

---

*This document explains every data source to a fresh agent. It implements the source hierarchy and multi-source composition rules.*
