# Urban Heat Intelligence — Evidence Provenance Teaching Document

**Document ID:** UHI-EVIDENCE-PROVENANCE-TEACHING-001
**Purpose:** Enable a fresh agent to understand the evidence provenance model.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Why Provenance Matters

The product's key differentiator is that every assertion carries source attribution. This is not a feature — it is an architectural invariant. An assertion without provenance is a bug.

---

## 2. The Evidence Receipt

Every tool response includes an evidence receipt:

```json
{
  "tool": "get_heatmap",
  "source": "fortyguard",
  "query_time": "2026-08-26T14:15:00Z",
  "cached": false,
  "confidence": 0.95,
  "mode": "live",
  "receipt_id": "fg-heatmap-20260826-141500",
  "parameters": {
    "area": "downtown_phoenix",
    "resolution": "2m"
  }
}
```

### 2.1 Required Fields

| Field | Meaning | Example |
|-------|---------|---------|
| tool | Which MCP tool produced this | get_heatmap |
| source | Which data provider | fortyguard |
| query_time | When the query was made | 2026-08-26T14:15:00Z |
| cached | Whether this was a cache hit | false |
| confidence | Agent's confidence in this data | 0.95 |
| mode | LIVE or REPLAY | live |
| receipt_id | Unique identifier for this receipt | fg-heatmap-20260826-141500 |

### 2.2 Optional Fields

| Field | When Present |
|-------|-------------|
| fixture_date | REPLAY mode — when the fixture was recorded |
| parameters | The query parameters used |
| parent_receipt_id | If this receipt is derived from another |
| staleness_seconds | If data is from cache, age in seconds |

---

## 3. The Evidence Log

All receipts are stored in the SQLite `evidence_log` table. This is append-only — receipts are never modified or deleted.

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

### 3.1 Evidence Log Rules

1. **Append-only** — receipts are never updated or deleted
2. **Every tool call** creates a receipt
3. **Every displayed assertion** must trace to a receipt
4. **The "Why?" panel** queries the evidence log to display the chain

---

## 4. The "Why?" Panel

When a user clicks "Why This Answer?", the agent displays the evidence chain:

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

Every line traces to a specific receipt.

---

## 5. Claim Taxonomy (SPEC-011)

The product uses 10 claim classes. Every displayed assertion must belong to one:

| Class | Example | Provenance Required |
|-------|---------|-------------------|
| SOURCE_OBSERVATION | "FortyGuard observed 42.05°C" | Source, tool, timestamp |
| DERIVED_CALCULATION | "Apparent temperature is 46.4°C" | Source, formula, inputs |
| COMPARATIVE_STATEMENT | "3 candidates within 0.1°C near-tie tolerance" | Candidate comparison, threshold |
| RECOMMENDATION | "These locations warrant comparable attention" | Product-derived decision note |
| CONTEXTUAL_NOTE | "NWS reports Partly Cloudy conditions" | Source, timestamp |
| PROVENANCE_DISCLOSURE | "NWS current context not included in historical Replay" | Source, mode |
| MODE_LABEL | "Live data" / "Replay data" | Mode determination |
| CONFIDENCE_DISCLOSURE | — | Not currently used |
| TEMPORAL_DISCLOSURE | "Data from 2:15 PM" | Timestamp source |
| UNSUPPORTED | [forbidden] | [must not appear] |

**The product must maintain 0 unsupported claims.** This is machine-verifiable.

---

## 6. Provenance for the Urban Heat Brief

The Heat Brief inherits the same provenance model. Every sentence in the brief traces to evidence:

The implemented Brief is returned in the answer payload as
`urban_heat_brief`. Each claim retains `claim_id`, `text`,
`source_provider`, `source_type`, `evidence_nodes`, `mode`,
`observation_time` and `used_in_decision`. FortyGuard claims support the
thermal decision. NWS claims are LIVE-only supplemental context and carry
`retrieved_at` plus an effective forecast period; they always have
`used_in_decision: false`. Replay includes an explicit NWS exclusion claim
and makes no NWS request.

| Brief Sentence | Evidence Trace |
|----------------|---------------|
| "FortyGuard identified the highest measured thermal burden among 367 evaluated heatmap features" | FortyGuard heatmap_result |
| "The leading candidate measured approximately 42.05°C against an area mean of 42.03°C" | FortyGuard heatmap_result + coordinate_selection |
| "FortyGuard environmental parameters report an apparent temperature of 46.40°C" | FortyGuard env_params_result |
| "3 candidate locations show effectively equivalent thermal burden" | UHI product-derived comparison (0.1°C threshold) |
| "Current NWS context is not included in historical Replay" | UHI nws_exclusion provenance disclosure |

**The narrative may simplify evidence. It may never invent or blur evidence.**

---

## 7. Provenance Integrity Tests

### 7.1 Receipt Completeness

| Test | Expected Result |
|------|----------------|
| Every tool call creates a receipt | PASS — evidence_log count matches tool call count |
| Every displayed assertion has a receipt | PASS — no orphan assertions |
| Receipt ID matches evidence_log entry | PASS — referential integrity |

### 7.2 Mode Integrity

| Test | Expected Result |
|------|----------------|
| LIVE receipts have query_time, not fixture_date | PASS |
| REPLAY receipts have fixture_date, not query_time | PASS |
| Mode label matches actual data source | PASS |

### 7.3 Claim Integrity

| Test | Expected Result |
|------|----------------|
| 0 unsupported claims in any response | PASS — machine-verifiable |
| Every claim class matches SPEC-011 taxonomy | PASS |
| Brief sentences trace to receipts | PASS |

### 7.4 "Why?" Panel Integrity

| Test | Expected Result |
|------|----------------|
| "Why?" panel shows all contributing receipts | PASS |
| Receipts match evidence_log | PASS |
| No fabricated evidence in chain | PASS |

---

## 8. Relationship to Other Teaching Documents

| Document | Relationship |
|----------|-------------|
| UHI-PRODUCT-TEACHING-001 | Provenance model is referenced in product overview |
| UHI-DECISION-FLOW-TEACHING-001 | Decision provenance follows these rules |
| UHI-LIVE-REPLAY-TEACHING-001 | Mode labels are part of provenance |
| UHI-DATA-SOURCES-TEACHING-001 | Source provenance is the foundation |
| SPEC-011 (claim taxonomy) | This document implements SPEC-011 |
| SPEC-012 (replay package) | Fixture provenance follows SPEC-012 |

---

*This document explains evidence provenance to a fresh agent. It implements the foundational invariant: every assertion carries source attribution.*
