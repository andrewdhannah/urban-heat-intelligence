# Urban Heat Intelligence — Provenance Model

**Version:** 1.1.0
**Date:** 2026-08-27
**Owner:** urban-heat-intelligence
**Status:** CURRENT — matches frozen implementation c13d8ea

---

## Core Invariant

Every displayed assertion carries source attribution. An assertion without provenance is a bug.

## Evidence Model (Implemented)

The application uses an in-memory evidence chain. There is no persistent database.

### Evidence Chain Structure

Each evidence node is a dict with:

```json
{
  "step": "string",
  "data": {},
  "timestamp": "ISO-8601"
}
```

The 8-node chain for a standard query is:

```
user_request → plan → heatmap_request → heatmap_result
→ coordinate_selection → env_params_request → env_params_result → answer
```

Additional nodes may appear:
- `nws_request` / `nws_result` / `nws_exclusion` — NWS context (LIVE only)
- `brief` — Urban Heat Brief composition metadata

### Evidence Chain Lifecycle

- Created fresh on each `HeatAgent.answer()` call
- Stored in `self.evidence_chain` (Python list)
- Serialized into the JSON API response via `build_visualization_payload()`
- Displayed in the browser "Inspect evidence +" panel
- **Not persisted** — no SQLite, no file storage, no database

### Evidence Panel Data Source

The "Inspect evidence +" panel renders the `evidence_chain` array from the JSON API response. Each chain node is displayed as a step name and detail text. The chain is the authoritative provenance record for the session.

## Claim Provenance (Urban Heat Brief)

The Urban Heat Brief uses a separate claim-level provenance model. Each claim retains:

```json
{
  "claim_id": "string",
  "text": "string",
  "source_provider": "FortyGuard | NWS | UHI",
  "source_type": "string (normative SPEC-011 class alias)",
  "evidence_nodes": ["string"],
  "mode": "live | replay",
  "observation_time": "ISO-8601",
  "retrieved_at": "ISO-8601 (NWS only)",
  "used_in_decision": true | false,
  "governing_threshold_celsius": 0.1 | null
}
```

This is machine-readable and inspectable in the browser DOM. The `source_type` field maps to the normative SPEC-011 taxonomy (see `qualification/specifications/UHI-SPEC-011-claim-taxonomy.md`).

## Claim Taxonomy (SPEC-011)

Normative claim taxonomy from UHI-SPEC-011 v1.0 (hash: 24b3ff87).
Canonical source: `qualification/specifications/UHI-SPEC-011-claim-taxonomy.md`.

| # | Normative Class | Source Required | Product Alias in Brief |
|---|----------------|----------------|----------------------|
| 1 | SOURCE_OBSERVATION | Yes — source, timestamp, spatial/temporal scope | thermal_measurement |
| 2 | NORMALIZED_OBSERVATION | Yes — source, original reference, schema version | — (mechanical normalization) |
| 3 | DERIVED_FINDING | Yes — all inputs, derivation method | product_derived_comparison |
| 4 | CORROBORATED_FINDING | Yes — 2+ independent sources | — (not currently produced) |
| 5 | HISTORICAL_COMPARISON | Yes — current + historical observations | — (NOAA deferred) |
| 6 | PRIORITY_CLASSIFICATION | Yes — calculation trace, factor values | product_derived_decision_note |
| 7 | INTERVENTION_RECOMMENDATION | Yes — derivation rules, conditions | — (deferred, not produced) |
| 8 | CONTEXTUAL_STATEMENT | Yes — source, publication date | official_current_context, provenance_disclosure |
| 9 | UNRESOLVED | Yes — question definition | — (not currently produced) |
| 10 | UNSUPPORTED | [forbidden] | [must not appear] |

**Zero unsupported claims rule:** Every factual Brief sentence must belong to one normative class (1-8). Classes 9-10 are structural. If a sentence cannot be mapped, it must not appear.

## Dependencies

The application uses Python stdlib only. No external runtime dependencies. `requirements.txt` is intentionally empty.

---

## Future Architecture (Target — Not Implemented)

The following represent potential future architecture, not current implementation:

### Persistent Evidence Log (Target)

If implemented in the future, evidence would be stored in an append-only SQLite table with schema:

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

This schema is NOT currently implemented. The in-memory evidence chain serves the same provenance purpose for the current product scope.

### Evidence Receipt Fields (Target)

If persistent receipts are implemented, each would include: `receipt_id`, `tool`, `source`, `query_time`, `cached`, `confidence`, `mode`. These fields are NOT present in the current in-memory evidence model.
