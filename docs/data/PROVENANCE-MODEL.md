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

Normative claim taxonomy from SPEC-011. The product uses these exact classes. Product-facing aliases in earlier teaching docs map to these normative classes.

| Normative Class | Source Required | Product Alias Used In Brief |
|----------------|----------------|---------------------------|
| SOURCE_OBSERVATION | Yes — tool, timestamp | thermal measurement |
| DERIVED_CALCULATION | Yes — formula, inputs | environmental measurement |
| COMPARATIVE_STATEMENT | Yes — both sources | product_derived_comparison |
| RECOMMENDATION | Yes — decision logic | product_derived_decision_note |
| CONTEXTUAL_NOTE | Yes — source, timestamp | official_current_context |
| ATTRIBUTED_CLAIM | Yes — source, layer | — (not currently used) |
| MODE_LABEL | Yes — mode determination | provenance_disclosure |
| CONFIDENCE_DISCLOSURE | Yes — calculation | — (not currently used) |
| TEMPORAL_DISCLOSURE | Yes — timestamp source | availability_disclosure |
| UNSUPPORTED | [forbidden] | [must not appear] |

**Machine-readable mapping:** The `source_type` field in each `urban_heat_brief.claims[]` entry uses the Product Alias column. These map one-to-one to the Normative Class column. No ambiguity exists.

**Zero unsupported claims rule:** Every factual Brief sentence must belong to one normative class above. If it cannot be mapped, it must not appear.

## "Why?" Panel

Displays the full evidence chain for any assertion. Every line traces to a receipt in the evidence log.

## Brief Provenance

Urban Heat Brief sentences trace to evidence receipts. Narrative may simplify evidence. It may never invent or blur evidence.
