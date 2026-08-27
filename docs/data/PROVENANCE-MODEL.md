# Urban Heat Intelligence — Provenance Model

**Version:** 1.0.0
**Date:** 2026-08-26
**Owner:** urban-heat-intelligence

---

## Core Invariant

Every displayed assertion carries source attribution. An assertion without provenance is a bug.

## Evidence Receipt

Every tool response includes:

```json
{
  "tool": "string",
  "source": "string",
  "query_time": "ISO-8601",
  "cached": "boolean",
  "confidence": "0.0-1.0",
  "mode": "live|replay",
  "receipt_id": "string"
}
```

## Evidence Log

Append-only SQLite table. Receipts are never modified or deleted.

```sql
CREATE TABLE evidence_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id TEXT UNIQUE NOT NULL,
    tool TEXT NOT NULL,
    source TEXT NOT NULL,
    query_time TEXT NOT NULL,
    cached BOOLEAN NOT NULL,
    confidence REAL,
    mode TEXT NOT NULL,
    receipt_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Claim Taxonomy (SPEC-011)

Normative claim taxonomy from UHI-SPEC-011 v1.0 (hash: 24b3ff87).
Canonical source: `qualification/specifications/UHI-SPEC-011-claim-taxonomy.md`.

| # | Normative Class | Source Required | Product Alias in Brief |
|---|----------------|----------------|----------------------|
| 1 | SOURCE_OBSERVATION | Yes — source, timestamp, spatial/temporal scope | thermal measurement |
| 2 | NORMALIZED_OBSERVATION | Yes — source, original reference, schema version | — (mechanical normalization) |
| 3 | DERIVED_FINDING | Yes — all inputs, derivation method | product_derived_comparison |
| 4 | CORROBORATED_FINDING | Yes — 2+ independent sources | — (not currently produced) |
| 5 | HISTORICAL_COMPARISON | Yes — current + historical observations | — (NOAA deferred) |
| 6 | PRIORITY_CLASSIFICATION | Yes — calculation trace, factor values | product_derived_decision_note |
| 7 | INTERVENTION_RECOMMENDATION | Yes — derivation rules, conditions | — (deferred, not produced) |
| 8 | CONTEXTUAL_STATEMENT | Yes — source, publication date | official_current_context, provenance_disclosure |
| 9 | UNRESOLVED | Yes — question definition | — (not currently produced) |
| 10 | UNSUPPORTED | [forbidden] | [must not appear] |

**Product-alias mapping:** The `source_type` field in each `urban_heat_brief.claims[]` entry uses aliases that map one-to-one to normative classes above. No ambiguity exists. Every factual Brief sentence must belong to exactly one normative class.

**Zero unsupported claims rule:** Every factual Brief sentence must belong to one normative class (1-8). Classes 9-10 are structural. If a sentence cannot be mapped, it must not appear.

## "Why?" Panel

Displays the full evidence chain for any assertion. Every line traces to a receipt in the evidence log.

## Brief Provenance

Urban Heat Brief sentences trace to evidence receipts. Narrative may simplify evidence. It may never invent or blur evidence.
