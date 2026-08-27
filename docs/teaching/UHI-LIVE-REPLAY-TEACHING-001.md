# Urban Heat Intelligence — Live/Replay Teaching Document

**Document ID:** UHI-LIVE-REPLAY-TEACHING-001
**Purpose:** Enable a fresh agent to understand the Live/Replay mode system and provenance integrity.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. Why Two Modes?

| Mode | Use Case | Credential Requirement |
|------|----------|----------------------|
| LIVE | Real-time analysis with current data | FORTYGUARD_API_KEY required |
| REPLAY | Demo, testing, offline use | Zero credentials — works out of the box |

REPLAY exists so the product is immediately demonstrable without API access. It uses genuine FortyGuard API responses recorded on Aug 25, 2026.

The current implementation also makes zero NWS network calls in Replay.
Current NWS context is explicitly excluded from the Replay Brief. NWS is
fetched only after a successful LIVE FortyGuard result and remains
`used_in_decision: false` supplemental context.

---

## 2. Architectural Rule

> **Live and Replay data must never contaminate each other.**

This is a hard invariant. A mixed-provenance display must be explicitly labeled. A Replay data point must never be presented as Live data, and vice versa.

---

## 3. Mode Detection

### 3.1 Response Labeling

Every tool response includes a `mode` field:

```json
{
  "tool": "get_heatmap",
  "source": "fortyguard",
  "mode": "live",
  "query_time": "2026-08-26T14:15:00Z",
  ...
}
```

or

```json
{
  "tool": "get_heatmap",
  "source": "fortyguard",
  "mode": "replay",
  "fixture_date": "2026-08-25",
  "query_time": "2026-08-25T14:15:00Z",
  ...
}
```

### 3.2 Display Rules

| Mode | Display Label | Colour | Timestamp Shown |
|------|--------------|--------|----------------|
| LIVE | "Live data" | Green | Current query time |
| REPLAY | "Replay data — Aug 25, 2026" | Amber/grey | Fixture date |

### 3.3 What the User Sees

**LIVE:**
```
🌡️ Live data — 2:15 PM MST
FortyGuard analysis of downtown Phoenix...
```

**REPLAY:**
```
📦 Replay data — Aug 25, 2026
FortyGuard analysis of downtown Phoenix (pre-recorded)...
```

---

## 4. Mixed Provenance Scenarios

### 4.1 When Mixed Provenance Can Occur

| Scenario | Result |
|----------|--------|
| REPLAY FortyGuard + LIVE NWS | Not produced by the current application; Replay excludes live NWS. |
| LIVE FortyGuard + NWS unavailable | LIVE label for FortyGuard. Brief discloses NWS unavailability and continues with thermal evidence. |
| REPLAY FortyGuard + all others unavailable | REPLAY label. Minimum brief with FortyGuard only. |

### 4.2 Mixed Provenance Display Rules

1. Each source carries its own mode label
2. The combined display shows all mode labels
3. Replay has no current NWS source; LIVE NWS, when available, is supplemental
4. The narrative (Heat Brief) must not blend modes without disclosure

### 4.3 What Is Forbidden

| Forbidden | Why |
|-----------|-----|
| Presenting Replay data as Live | Violates provenance integrity |
| Omitting mode label from any source | User cannot assess data freshness |
| Mixing modes in a single assertion | Each assertion must have clear provenance |
| "Upgrading" Replay to Live after verification | Mode is determined at query time, not after |

---

## 5. Fixture Management

### 5.1 Fixture Sources

| Fixture | Source | Date | Contents |
|---------|--------|------|----------|
| Heatmap response | FortyGuard /v1/heatmap | Aug 25, 2026 | 367 thermal features, Phoenix area |
| Environment parameters | FortyGuard /v1/env_params | Aug 25, 2026 | Temperature, humidity, wind, apparent temp |
| NWS conditions | NWS API | LIVE retrieval only | Current conditions, advisories |
| System API key usage | FortyGuard /v1/system/fetch-api-key-usage | Diagnostic only | Credential/entitlement check, not product Brief evidence |

### 5.2 Fixture Integrity

- Fixtures are stored in the repository
- SHA-256 hashes verify fixture integrity (SPEC-012)
- Fixtures are versioned — changes produce new fixture versions
- The product must not modify fixtures at runtime

### 5.3 Fixture Date Disclosure

The fixture date is always visible to the user:
- In REPLAY mode label
- In the "Why?" evidence panel
- In any exported Brief or report

---

## 6. QA Implications

### 6.1 Mode Correctness Tests

| Test | Expected Result |
|------|----------------|
| REPLAY mode produces labeled responses | PASS — all responses carry `mode: "replay"` |
| LIVE mode produces labeled responses | PASS — all responses carry `mode: "live"` |
| Mixed mode display shows all labels | PASS — each source labeled individually |
| No unlabeled data reaches the UI | PASS — every displayed data point has mode |

### 6.2 Provenance Integrity Tests

| Test | Expected Result |
|------|----------------|
| REPLAY data has fixture_date, not query_time | PASS |
| LIVE data has query_time, not fixture_date | PASS |
| Evidence log records mode for every entry | PASS |
| "Why?" panel shows mode for each source | PASS |

### 6.3 Contamination Tests

| Test | Expected Result |
|------|----------------|
| No Replay data appears in LIVE session | PASS |
| No Live data appears in REPLAY session | PASS |
| Mixed session labels each source independently | PASS |

---

## 7. Relationship to Other Teaching Documents

| Document | Relationship |
|----------|-------------|
| UHI-PRODUCT-TEACHING-001 | This document specifies the mode system referenced in Section 5 of the product teaching doc |
| UHI-EVIDENCE-PROVENANCE-TEACHING-001 | Mode labels are part of the evidence provenance model |
| UHI-FAILURE-STATES-TEACHING-001 | Provider unavailability is a failure state that may force mode mixing |
| SPEC-012 (Replay Package) | Fixtures must conform to SPEC-012 replay package contract |

---

*This document explains the Live/Replay system to a fresh agent. It implements the provenance integrity invariant.*
