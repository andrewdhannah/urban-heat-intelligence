# UHI-SPEC-010: Intervention Rule Specification

**Version:** 1.0
**Date:** 2026-08-21
**Status:** NORMATIVE — Testable Specification

---

## 1. Purpose

Define deterministic intervention derivation rules that can be independently verified by QA-Pilot.

## 2. Intervention Categories

### 2.1 Shade/Canopy Intervention

**Trigger:** High thermal burden + low canopy + high impervious surface + high solar exposure

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Heat Burden Score | Derived | ≥ 0.50 |
| Canopy Percentage | USGS/NLCD | < 15% |
| Impervious Surface | USGS/NLCD | > 50% |
| Solar Irradiance | FortyGuard env_params | > 600 W/m² |

**Derivation Rule:**
```
IF Heat_Burden ≥ 0.50
   AND Canopy_Percentage < 15
   AND Impervious_Surface > 50
   AND Solar_Irradiance > 600
THEN recommend SHADE_CANOPY
```

**Recommendation:** Plant trees, install shade structures, create green corridors

### 2.2 Cool Surface Intervention

**Trigger:** High thermal burden + high impervious surface + low canopy + urban area

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Heat Burden Score | Derived | ≥ 0.50 |
| Impervious Surface | USGS/NLCD | > 60% |
| Canopy Percentage | USGS/NLCD | < 10% |
| Land Cover Classification | USGS/NLCD | Urban |

**Derivation Rule:**
```
IF Heat_Burden ≥ 0.50
   AND Impervious_Surface > 60
   AND Canopy_Percentage < 10
   AND Land_Cover = "urban"
THEN recommend COOL_SURFACE
```

**Recommendation:** Apply cool pavement coatings, reflective roofing, cool surfaces

### 2.3 Cooling Center Intervention

**Trigger:** High thermal burden + high population + no cooling infrastructure

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Heat Burden Score | Derived | ≥ 0.60 |
| Population Density | Census | > 2000/km² |
| Cooling Center Within 1 Mile | Local context | false |
| Green Space Within 0.5 Mile | USGS/NLCD | false |

**Derivation Rule:**
```
IF Heat_Burden ≥ 0.60
   AND Population_Density > 2000
   AND Cooling_Center_Within_1Mile = false
   AND Green_Space_Within_0_5Mile = false
THEN recommend COOLING_CENTER
```

**Recommendation:** Establish or expand cooling center access

### 2.4 Green Infrastructure Intervention

**Trigger:** Moderate thermal burden + low vegetation + high impervious

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Heat Burden Score | Derived | ≥ 0.35 |
| Vegetation Percentage | USGS/NLCD | < 20% |
| Impervious Surface | USGS/NLCD | > 40% |
| Available Land | Local context | Available |

**Derivation Rule:**
```
IF Heat_Burden ≥ 0.35
   AND Vegetation_Percentage < 20
   AND Impervious_Surface > 40
   AND Available_Land = true
THEN recommend GREEN_INFRASTRUCTURE
```

**Recommendation:** Install green roofs, rain gardens, bioswales, urban gardens

### 2.5 Early Warning System Intervention

**Trigger:** High heat persistence + limited monitoring + high population

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Heat Persistence Score | Derived | ≥ 0.50 |
| Population Density | Census | > 1500/km² |
| Weather Station Density | Local context | < 1 per 5 km² |

**Derivation Rule:**
```
IF Heat_Persistence ≥ 0.50
   AND Population_Density > 1500
   AND Weather_Station_Density < 0.2
THEN recommend EARLY_WARNING
```

**Recommendation:** Deploy temperature monitoring, establish heat alert protocols

### 2.6 Policy/Planning Intervention

**Trigger:** Consistent historical trend + high burden + jurisdiction available

**Required Evidence:**
| Evidence | Source | Threshold |
|----------|--------|-----------|
| Historical Temperature Trend | NOAA/NCEI | Increasing (≥ 0.5°C/decade) |
| Heat Burden Score | Derived | ≥ 0.40 |
| Municipal Jurisdiction | Local context | Available |

**Derivation Rule:**
```
IF Historical_Trend ≥ 0.5
   AND Heat_Burden ≥ 0.40
   AND Municipal_Jurisdiction = true
THEN recommend POLICY_PLANNING
```

**Recommendation:** Develop heat action plan, update building codes, zoning changes

---

## 3. Conflict Handling

### 3.1 Multiple Interventions

When multiple interventions are triggered:
1. List all triggered interventions
2. Rank by evidence strength (number of conditions met)
3. Present all with confidence levels

### 3.2 Conflicting Evidence

When evidence conflicts:
1. Flag the conflict
2. Present both sides with evidence
3. Do not resolve automatically
4. Require Owner decision

---

## 4. Insufficient Evidence

### 4.1 Missing Evidence Behavior

When required evidence is missing:
1. Do not recommend the intervention
2. Record "Insufficient evidence for [intervention]"
3. List missing evidence components
4. Set recommendation confidence to 0

### 4.2 Partial Evidence

When some evidence is available:
1. Calculate partial confidence
2. If confidence ≥ 70%, recommend with caveat
3. If confidence < 70%, do not recommend

---

## 5. Recommendation Output

### 5.1 Recommendation Structure

```json
{
  "intervention_type": "shade_canopy",
  "confidence": 0.85,
  "evidence_summary": [
    "Heat Burden: 0.72 (severe)",
    "Canopy: 8% (low)",
    "Impervious: 65% (high)",
    "Solar: 720 W/m² (high)"
  ],
  "derivation_trace": {
    "factors_used": ["heat_burden", "canopy", "impervious", "solar"],
    "thresholds_met": 4,
    "thresholds_required": 4
  },
  "recommendation": "Plant trees, install shade structures, create green corridors"
}
```

### 5.2 Explanation Requirements

Every recommendation must include:
- Which factors triggered it
- What thresholds were met
- What evidence supports it
- What confidence level exists

---

## 6. Provenance Requirements

### 6.1 Required Provenance

Every intervention derivation must record:
- Input evidence references
- Factor values used
- Threshold values applied
- Calculation result
- Confidence score
- Timestamp
- Specification version

### 6.2 Audit Trail

Intervention derivation is auditable:
- Same inputs → same recommendations
- All thresholds documented
- All evidence referenced

---

## 7. Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-21 | Initial specification |

---

*Specification complete. Testable by QA-Pilot.*
