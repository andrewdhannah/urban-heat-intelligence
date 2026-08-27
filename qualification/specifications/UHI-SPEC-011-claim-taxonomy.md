# UHI-SPEC-011: Claim Taxonomy Specification

**Version:** 1.0
**Date:** 2026-08-21
**Status:** NORMATIVE — Testable Specification

---

## 1. Purpose

Define a normative claim taxonomy for urban heat analysis, making "0 unsupported claims" a machine-verifiable result.

## 2. Claim Classes

### 2.1 SOURCE_OBSERVATION

**Meaning:** A direct observation from a qualified source.

**Required evidence references:**
- Source identity (provider/dataset)
- Observation timestamp
- Spatial scope
- Temporal validity

**Required derivation references:** None

**Corroboration required:** No

**May be displayed as verified:** Yes

**Temporal/spatial provenance:** Required

**Treatment in unsupported-claim calculation:** Supported if evidence present

### 2.2 NORMALIZED_OBSERVATION

**Meaning:** A source observation that has been normalized to the common evidence schema.

**Required evidence references:**
- Source identity
- Original observation reference
- Normalization timestamp
- Normalized schema version

**Required derivation references:** None (normalization is mechanical)

**Corroboration required:** No

**May be displayed as verified:** Yes

**Temporal/spatial provenance:** Inherited from source

**Treatment in unsupported-claim calculation:** Supported if source observation present

### 2.3 DERIVED_FINDING

**Meaning:** An analytical finding derived from multiple observations.

**Required evidence references:**
- All source observations used
- Normalized observations used

**Required derivation references:**
- Derivation method
- Input factors
- Calculation result

**Corroboration required:** No (but corroboration noted if present)

**May be displayed as verified:** Yes, with derivation trace

**Temporal/spatial provenance:** Inherited from source observations

**Treatment in unsupported-claim calculation:** Supported if derivation trace complete

### 2.4 CORROBORATED_FINDING

**Meaning:** A finding supported by multiple independent sources.

**Required evidence references:**
- All corroborating source observations
- All corroborating normalized observations

**Required derivation references:**
- Corroboration method
- Source independence verification

**Corroboration required:** Yes (minimum 2 independent sources)

**May be displayed as verified:** Yes, with corroboration evidence

**Temporal/spatial provenance:** Required from all sources

**Treatment in unsupported-claim calculation:** Supported if 2+ independent sources

### 2.5 HISTORICAL_COMPARISON

**Meaning:** A comparison between current and historical conditions.

**Required evidence references:**
- Current observation
- Historical observation
- Time period defined

**Required derivation references:**
- Comparison method
- Trend calculation

**Corroboration required:** No

**May be displayed as verified:** Yes, with temporal provenance

**Temporal/spatial provenance:** Required (both current and historical)

**Treatment in unsupported-claim calculation:** Supported if both observations present

### 2.6 PRIORITY_CLASSIFICATION

**Meaning:** A zone priority ranking based on derived analysis.

**Required evidence references:**
- All evidence used in priority calculation
- Priority score

**Required derivation references:**
- Priority calculation method
- Factor values
- Weights used

**Corroboration required:** No

**May be displayed as verified:** Yes, with calculation trace

**Temporal/spatial provenance:** Inherited from source evidence

**Treatment in unsupported-claim calculation:** Supported if calculation trace complete

### 2.7 INTERVENTION_RECOMMENDATION

**Meaning:** A recommended action based on analysis.

**Required evidence references:**
- All evidence supporting the recommendation
- Intervention type

**Required derivation references:**
- Intervention derivation rules
- Conditions met
- Confidence level

**Corroboration required:** No

**May be displayed as verified:** Yes, with derivation trace

**Temporal/spatial provenance:** Inherited from source evidence

**Treatment in unsupported-claim calculation:** Supported if derivation trace complete

### 2.8 CONTEXTUAL_STATEMENT

**Meaning:** Contextual information that supplements analysis but is not a factual claim.

**Required evidence references:**
- Source identity
- Publication date

**Required derivation references:** None

**Corroboration required:** No

**May be displayed as verified:** No (displayed as "Contextual")

**Temporal/spatial provenance:** Recommended

**Treatment in unsupported-claim calculation:** Not counted as claim

### 2.9 UNRESOLVED

**Meaning:** A question that has been identified but not yet answered.

**Required evidence references:**
- Question definition
- Why it's unresolved

**Required derivation references:** None

**Corroboration required:** No

**May be displayed as verified:** No (displayed as "Unresolved")

**Temporal/spatial provenance:** Not required

**Treatment in unsupported-claim calculation:** Not counted as claim

### 2.10 UNSUPPORTED

**Meaning:** A claim that lacks sufficient evidence.

**Required evidence references:** None (that's the problem)

**Required derivation references:** None

**Corroboration required:** No

**May be displayed as verified:** No (must be flagged)

**Temporal/spatial provenance:** Not applicable

**Treatment in unsupported-claim calculation:** Counted as unsupported

---

## 3. Claim Registry Rules

### 3.1 Registration

Every claim must be registered with:
- Claim class
- Claim text
- Evidence references
- Derivation references
- Support status

### 3.2 Support Status

| Status | Meaning | Display Treatment |
|--------|---------|-------------------|
| supported | Evidence confirms claim | "Verified" |
| partially_supported | Some evidence, gaps exist | "Partially verified" |
| unsupported | Insufficient evidence | "Unsupported" (flagged) |
| contradicted | Evidence conflicts | "Contradicted" (flagged) |
| contextual | Not a factual claim | "Contextual" |
| unresolved | Question identified | "Unresolved" |

### 3.3 Unsupported Claim Calculation

**Formula:**
```
Unsupported Claims = Count of claims where support_status = "unsupported"
```

**Invariant:** "0 unsupported claims" must be machine-verifiable.

### 3.4 Claim Lifecycle

```
Registration → Evidence Linking → Support Assessment → Status Assignment
```

---

## 4. Evidence Reference Requirements

### 4.1 Minimum Evidence

Every factual claim (classes 1-7) must have at least one evidence reference.

### 4.2 Evidence Reference Structure

```json
{
  "evidence_id": "uuid",
  "source": "provider/dataset",
  "timestamp": "ISO 8601",
  "spatial_scope": {
    "type": "polygon|point",
    "coordinates": [...]
  },
  "temporal_scope": {
    "start": "ISO 8601",
    "end": "ISO 8601"
  }
}
```

---

## 5. Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-21 | Initial specification |

---

*Specification complete. Testable by QA-Pilot.*
