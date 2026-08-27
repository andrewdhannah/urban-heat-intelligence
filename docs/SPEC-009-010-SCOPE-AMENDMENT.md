# SPEC-009 / SPEC-010 Qualification Scope Amendment

**Date:** 2026-08-27
**Authority:** S3D reconciliation
**Purpose:** Record what was implemented vs. what remains in the broader normative specifications.

---

## SPEC-009 — Heat Burden × Intervention Opportunity Model

**Normative scope:** A multi-factor scoring model combining Heat Burden (Thermal Severity, Heat Persistence, Exposure Factor, Deviation Score) with Intervention Opportunity (Cooling Deficit, Intervention Surface, Social Equity, Population Exposure, Existing Governance).

### Hackathon Implemented Subset

- FortyGuard thermal ranking
- Deterministic descending observed temperature
- Top-3 candidate comparison
- Delta from area mean
- env_params context (heat index, apparent, humidity)
- Explicit 0.1°C near-tie semantics

### Not Implemented

- Full intervention-opportunity factor model (CD, ISL, SE, PE, EIG)
- Weighted multi-factor scoring formula
- Confidence threshold (60%)
- Missing-data proportional reduction

### Reason

Authoritative intervention-opportunity evidence (Phoenix GIS, demographic data, city data) was not integrated within hackathon scope.

### Governance Rule

Absence must remain explicit. Do not claim full SPEC-009 implementation.

---

## SPEC-010 — Intervention Category Derivation

**Normative scope:** Six intervention categories (Shade/Canopy, Cool Surface, Cooling Center, Green Infrastructure, Early Warning, Policy/Planning) derived from threshold-based applicability scoring.

### Hackathon Implemented Subset

- Bounded decision-support language based on measured thermal evidence
- Candidate ranking for investigation prioritization
- Near-tie disclosure

### Not Implemented

- Six-category threshold-derived intervention model
- Category-specific applicability scoring
- SPEC-010 rule-based intervention selection

### Reason

Intervention category selection requires GIS, demographic, and policy context not integrated in the hackathon.

### Governance Rule

Do not claim SPEC-010 implementation. The product recommends where to investigate, not what intervention to deploy.

---

## Classification for S3E

Final S3E may qualify the implemented behavior and classify the unimplemented broader obligations as known limitations / deferred scope. Do not silently mark original obligations PASS.
