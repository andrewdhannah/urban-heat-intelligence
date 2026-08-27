# UHI-SPEC-009: Priority and Ranking Specification

**Version:** 1.0
**Date:** 2026-08-21
**Status:** NORMATIVE — Testable Specification

---

## 1. Purpose

Define a deterministic, independently reproducible priority scoring system for urban heat analysis zones.

## 2. Conceptual Separation

### 2.1 Heat Burden

**Question:** How severe and persistent is the thermal condition?

**Factors:**
- Temperature severity
- Heat persistence
- Exceedance frequency
- Duration of extreme conditions

### 2.2 Intervention Opportunity

**Question:** How suitable or necessary is a particular intervention?

**Factors:**
- Physical conditions (canopy, impervious, solar)
- Existing infrastructure
- Population exposure
- Cost-effectiveness potential

### 2.3 Combined Priority

**Formula:** `Priority = Heat Burden × Intervention Opportunity`

**Note:** These are separate dimensions, not a single opaque number.

---

## 3. Heat Burden Factors

### 3.1 Factor: Temperature Severity (TS)

**Definition:** How extreme is the temperature relative to historical norms?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "temperature_severity" |
| value | number | yes | Observed temperature (°C) |
| baseline | number | yes | Historical average for same location/date |
| unit | string | yes | "celsius" |

**Calculation:**
```
TS = clamp((value - baseline) / 15, 0, 1)
```

**Range:** 0.0 (at baseline) to 1.0 (15°C+ above baseline)

**Evidence sources:** FortyGuard `/v1/heatmap`, NOAA/NCEI historical

### 3.2 Factor: Heat Persistence (HP)

**Definition:** How many consecutive days exceed the threshold?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "heat_persistence" |
| consecutive_days | number | yes | Days with max temp ≥ threshold |
| threshold | number | yes | Temperature threshold (°C) |

**Calculation:**
```
HP = clamp(consecutive_days / 7, 0, 1)
```

**Range:** 0.0 (0 days) to 1.0 (7+ days)

**Evidence sources:** FortyGuard `/v1/heatmap` with `filter_type: 4`

### 3.3 Factor: Exceedance Frequency (EF)

**Definition:** What percentage of observations exceed the threshold?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "exceedance_frequency" |
| exceedance_count | number | yes | Observations exceeding threshold |
| total_observations | number | yes | Total observations |
| threshold | number | yes | Temperature threshold (°C) |

**Calculation:**
```
EF = exceedance_count / total_observations
```

**Range:** 0.0 (never exceeds) to 1.0 (always exceeds)

**Evidence sources:** FortyGuard `/v1/heatmap` with `analytic_type: "exceedance"`

### 3.4 Factor: Duration Score (DS)

**Definition:** What is the typical daily duration of extreme heat?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "duration_score" |
| hours_above_threshold | number | yes | Average hours per day above threshold |
| threshold | number | yes | Temperature threshold (°C) |

**Calculation:**
```
DS = clamp(hours_above_threshold / 12, 0, 1)
```

**Range:** 0.0 (0 hours) to 1.0 (12+ hours)

**Evidence sources:** FortyGuard `/v1/heatmap` with `filter_type: 2`

### 3.5 Heat Burden Score

**Formula:**
```
HB = (TS × 0.4) + (HP × 0.25) + (EF × 0.2) + (DS × 0.15)
```

**Weights:**
| Factor | Weight | Rationale |
|--------|--------|-----------|
| Temperature Severity | 0.40 | Most direct measure of heat impact |
| Heat Persistence | 0.25 | Extended exposure increases health risk |
| Exceedance Frequency | 0.20 | Regularity indicates systematic problem |
| Duration Score | 0.15 | Daily duration affects outdoor activity |

**Range:** 0.0 to 1.0

---

## 4. Intervention Opportunity Factors

### 4.1 Factor: Canopy Deficit (CD)

**Definition:** How much tree canopy coverage is missing relative to target?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "canopy_deficit" |
| current_canopy | number | yes | Current tree canopy percentage |
| target_canopy | number | yes | Target canopy percentage |

**Calculation:**
```
CD = clamp((target_canopy - current_canopy) / target_canopy, 0, 1)
```

**Range:** 0.0 (at target) to 1.0 (no canopy)

**Evidence sources:** USGS/NLCD Tree Canopy Cover

### 4.2 Factor: Impervious Surface Load (ISL)

**Definition:** How much impervious surface exists?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "impervious_surface_load" |
| impervious_percentage | number | yes | Impervious surface percentage |

**Calculation:**
```
ISL = clamp(impervious_percentage / 80, 0, 1)
```

**Range:** 0.0 (0% impervious) to 1.0 (80%+ impervious)

**Evidence sources:** USGS/NLCD Impervious Surface

### 4.3 Factor: Solar Exposure (SE)

**Definition:** How much solar irradiance does the location receive?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "solar_exposure" |
| ghi | number | yes | Global Horizontal Irradiance (W/m²) |

**Calculation:**
```
SE = clamp(ghi / 800, 0, 1)
```

**Range:** 0.0 (0 W/m²) to 1.0 (800+ W/m²)

**Evidence sources:** FortyGuard `/v1/env_params` solar_irradiance

### 4.4 Factor: Population Exposure (PE)

**Definition:** How many people are exposed to this zone?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "population_exposure" |
| population_density | number | yes | People per km² |

**Calculation:**
```
PE = clamp(population_density / 5000, 0, 1)
```

**Range:** 0.0 (uninhabited) to 1.0 (5000+ people/km²)

**Evidence sources:** Census Bureau, local context

### 4.5 Factor: Existing Infrastructure Gap (EIG)

**Definition:** Is cooling infrastructure present?

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | "existing_infrastructure_gap" |
| has_cooling_center | boolean | yes | Cooling center within 1 mile |
| has_green_space | boolean | yes | Park or green space within 0.5 mile |

**Calculation:**
```
EIG = (1 if !has_cooling_center else 0) × 0.6 + (1 if !has_green_space else 0) × 0.4
```

**Range:** 0.0 (both present) to 1.0 (neither present)

**Evidence sources:** Web Search + Biblio, local context

### 4.6 Intervention Opportunity Score

**Formula:**
```
IO = (CD × 0.30) + (ISL × 0.25) + (SE × 0.20) + (PE × 0.15) + (EIG × 0.10)
```

**Weights:**
| Factor | Weight | Rationale |
|--------|--------|-----------|
| Canopy Deficit | 0.30 | Most effective cooling intervention |
| Impervious Surface | 0.25 | Direct contributor to heat island |
| Solar Exposure | 0.20 | Energy input driver |
| Population Exposure | 0.15 | Human impact multiplier |
| Infrastructure Gap | 0.10 | Existing resources reduce intervention need |

**Range:** 0.0 to 1.0

---

## 5. Combined Priority Score

### 5.1 Formula

```
Priority = Heat Burden × Intervention Opportunity
```

**Range:** 0.0 to 1.0

### 5.2 Priority Classification

| Score Range | Classification | Meaning |
|-------------|----------------|---------|
| 0.00 – 0.25 | Low | Minimal heat burden or limited intervention opportunity |
| 0.25 – 0.50 | Moderate | Significant burden with some intervention potential |
| 0.50 – 0.75 | High | Severe burden with strong intervention potential |
| 0.75 – 1.00 | Critical | Extreme burden requiring immediate attention |

### 5.3 Ranking Rules

1. Zones ranked by Priority score (descending)
2. Ties broken by Heat Burden score (descending)
3. Secondary ties broken by Intervention Opportunity score (descending)
4. Tertiary ties broken by zone name (alphabetical)

---

## 6. Missing Value Policy

### 6.1 Missing Factor Values

When a factor value is missing:

1. Set factor to 0.0
2. Record `missing_reason` in provenance
3. Reduce confidence score

### 6.2 Confidence Score

```
Confidence = (number of available factors / total factors) × 100
```

**Minimum threshold:** 60% confidence required for priority classification

Below 60% confidence, zone is classified as "Insufficient Data"

---

## 7. Deterministic Calculation Rules

### 7.1 Invariants

- Same inputs always produce same output
- No random or time-dependent components
- No external API calls during calculation
- All intermediate values stored for audit

### 7.2 Audit Trail

Every calculation produces:
- Input values for each factor
- Intermediate calculation results
- Final priority score
- Confidence score
- Timestamp of calculation
- Version of specification used

---

## 8. Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-21 | Initial specification |

---

*Specification complete. Testable by QA-Pilot.*
