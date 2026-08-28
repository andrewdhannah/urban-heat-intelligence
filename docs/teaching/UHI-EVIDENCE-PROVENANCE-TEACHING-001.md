# Urban Heat Intelligence — Evidence Provenance Teaching Document

**Document ID:** UHI-EVIDENCE-PROVENANCE-TEACHING-001
**Purpose:** Enable a fresh agent to understand the evidence provenance model.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Why Provenance Matters

The product's key differentiator is that every assertion carries source attribution. This is not a feature — it is an architectural invariant. An assertion without provenance is a bug.

---

## 2. The Evidence Chain (Implemented)

The application uses an in-memory evidence chain — not a database. Each `HeatAgent.answer()` call creates a fresh chain that is serialized into the JSON API response.

### 2.1 Evidence Node Structure

```json
{
  "step": "heatmap_result",
  "data": { "tool": "get_heatmap", "feature_count": 367, ... },
  "timestamp": "2026-08-26T14:15:00+00:00"
}
```

| Field | Meaning | Example |
|-------|---------|---------|
| step | Which pipeline stage produced this | heatmap_result |
| data | Payload specific to that stage | tool call result |
| timestamp | When the node was created | ISO-8601 |

### 2.2 Standard 8-Node Chain

```
user_request → plan → heatmap_request → heatmap_result
→ coordinate_selection → env_params_request → env_params_result → answer
```

Additional nodes may appear:
- `nws_request` / `nws_result` / `nws_exclusion` — NWS context (LIVE only)
- `brief` — Urban Heat Brief composition metadata

### 2.3 Evidence Chain Lifecycle

1. Created fresh on each `HeatAgent.answer()` call
2. Stored in `self.evidence_chain` (Python list)
3. Serialized into the JSON API response via `build_visualization_payload()`
4. Displayed in the browser "Inspect evidence +" panel
5. **Not persisted** — no SQLite, no file storage, no database

### 2.4 Future Target (Not Implemented)

If persistent evidence storage were implemented, receipts would include `receipt_id`, `cached`, `confidence`, and `query_time` fields. These are NOT present in the current in-memory model.

---

## 3. The "Why?" Panel

When a user clicks "Inspect evidence +", the agent displays the evidence chain:

```text
Why is Candidate #1 the first to investigate?

FortyGuard heatmap (Replay, Aug 25 2026 14:00 MST)
  → 367 features analyzed
  → Top feature: 42.05°C at [coordinate]
  → Area mean: 42.03°C

FortyGuard env_params (Replay, Aug 25 2026 14:00 MST)
  → Apparent temperature: 46.4°C
  → Humidity: 11.3%
  → Heat index: 39.3°C

Candidate comparison (product-derived):
  → 3 candidates within 0.1°C near-tie tolerance
  → Thermal evidence alone does not support meaningful distinction

NWS (excluded in Replay):
  → "Current NWS context is not included in historical Replay."
```

Every line traces to a step in the evidence chain.

---

## 4. Claim Taxonomy (SPEC-011)

The product uses 10 normative claim classes from UHI-SPEC-011. Every displayed assertion must belong to one:

| # | Normative Class | Source Required |
|---|----------------|----------------|
| 1 | SOURCE_OBSERVATION | Yes — source, timestamp |
| 2 | NORMALIZED_OBSERVATION | Yes — source, original reference |
| 3 | DERIVED_FINDING | Yes — all inputs, derivation method |
| 4 | CORROBORATED_FINDING | Yes — 2+ independent sources |
| 5 | HISTORICAL_COMPARISON | Yes — current + historical |
| 6 | PRIORITY_CLASSIFICATION | Yes — calculation trace |
| 7 | INTERVENTION_RECOMMENDATION | Yes — derivation rules |
| 8 | CONTEXTUAL_STATEMENT | Yes — source, publication date |
| 9 | UNRESOLVED | Yes — question definition |
| 10 | UNSUPPORTED | [forbidden] |

**The product must maintain 0 unsupported claims.** This is machine-verifiable.

---

## 5. Provenance for the Urban Heat Brief

The Heat Brief inherits the same provenance model. Every sentence in the brief traces to evidence:

The Brief is returned in the answer payload as `urban_heat_brief`. Each claim retains `claim_id`, `text`, `source_provider`, `source_type`, `evidence_nodes`, `mode`, `observation_time` and `used_in_decision`. FortyGuard claims support the thermal decision. NWS claims are LIVE-only supplemental context and carry `retrieved_at` plus an effective forecast period; they always have `used_in_decision: false`. Replay includes an explicit NWS exclusion claim and makes no NWS request.

| Brief Sentence | Evidence Trace |
|----------------|---------------|
| "FortyGuard identified the highest measured thermal burden among 367 evaluated heatmap features" | FortyGuard heatmap_result |
| "The leading candidate measured approximately 42.05°C against an area mean of 42.03°C" | FortyGuard heatmap_result + coordinate_selection |
| "FortyGuard environmental parameters report an apparent temperature of 46.40°C" | FortyGuard env_params_result |
| "3 candidate locations show effectively equivalent thermal burden" | UHI product-derived comparison (0.1°C threshold) |
| "Current NWS context is not included in historical Replay" | UHI nws_exclusion provenance disclosure |

**The narrative may simplify evidence. It may never invent or blur evidence.**

---

## 6. Provenance Integrity Tests

### 6.1 Chain Completeness

| Test | Expected Result |
|------|----------------|
| Every evidence node has a step and data | PASS — structurally validated |
| Chain length >= 8 for standard query | PASS — 8+ nodes |
| Every displayed assertion has a chain trace | PASS — no orphan assertions |

### 6.2 Mode Integrity

| Test | Expected Result |
|------|----------------|
| LIVE chain includes NWS nodes | PASS |
| REPLAY chain includes nws_exclusion node | PASS |
| Mode label matches actual data source | PASS |
| Visualization source matches mode | PASS |

### 6.3 Claim Integrity

| Test | Expected Result |
|------|----------------|
| 0 unsupported claims in any Brief | PASS — machine-verifiable |
| Every claim source_type maps to normative SPEC-011 class | PASS |
| Brief sentences trace to evidence nodes | PASS |

### 6.4 "Why?" Panel Integrity

| Test | Expected Result |
|------|----------------|
| "Why?" panel shows all chain nodes | PASS |
| Chain nodes match API response | PASS |
| No fabricated evidence in chain | PASS |

---

## 7. Relationship to Other Teaching Documents

| Document | Relationship |
|----------|-------------|
| UHI-PRODUCT-TEACHING-001 | Provenance model is referenced in product overview |
| UHI-DECISION-FLOW-TEACHING-001 | Decision provenance follows these rules |
| UHI-LIVE-REPLAY-TEACHING-001 | Mode labels are part of provenance |
| UHI-DATA-SOURCES-TEACHING-001 | Source provenance is the foundation |
| SPEC-011 (claim taxonomy) | This document implements SPEC-011 |
| SPEC-012 (replay package) | Fixture provenance follows SPEC-012 |

---

*This document explains the evidence provenance model to a fresh agent. It matches the frozen implementation c13d8ea.*
