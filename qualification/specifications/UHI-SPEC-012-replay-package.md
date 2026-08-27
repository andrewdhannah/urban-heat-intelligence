# UHI-SPEC-012: Replay Package Contract

**Version:** 1.0
**Date:** 2026-08-21
**Status:** NORMATIVE — Testable Specification

---

## 1. Purpose

Define a normative replay package/fixture specification that represents captured governed execution evidence, not handcrafted demo data.

## 2. Package Structure

### 2.1 Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| package_id | UUID | yes | Unique package identifier |
| schema_version | string | yes | Contract version (e.g., "1.0.0") |
| capture_timestamp | ISO 8601 | yes | When package was captured |
| original_analysis_request | object | yes | The request that triggered the analysis |
| provider_executions | array | yes | List of provider executions |
| raw_responses | array | no | Raw API responses (where permitted) |
| normalized_evidence | array | yes | Normalized evidence records |
| source_provenance | array | yes | Source/provenance records |
| artifacts | array | yes | Generated artifacts |
| hashes | object | yes | Integrity hashes |
| receipts | array | yes | Governance receipts |
| expected_analysis | object | yes | Expected UrbanHeatAnalysis output |
| integrity_manifest | object | yes | Package integrity manifest |

### 2.2 Package Identity

```json
{
  "package_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema_version": "1.0.0",
  "capture_timestamp": "2026-08-21T12:00:00Z",
  "captured_by": "qa-pilot",
  "project_id": "urban-heat-intelligence"
}
```

### 2.3 Original Analysis Request

```json
{
  "location": {
    "name": "Phoenix, AZ",
    "polygon": {
      "type": "FeatureCollection",
      "features": []
    }
  },
  "analysis_types": ["thermal_burden", "intervention_opportunity"],
  "time_range": {
    "start": "2026-07-01",
    "end": "2026-07-31"
  }
}
```

### 2.4 Provider Executions

```json
{
  "provider_executions": [
    {
      "provider": "fortyguard",
      "endpoint": "/v1/heatmap",
      "activity_id": "uuid",
      "request_timestamp": "ISO 8601",
      "response_timestamp": "ISO 8601",
      "status": "completed",
      "response_hash": "sha256:..."
    }
  ]
}
```

### 2.5 Normalized Evidence

```json
{
  "normalized_evidence": [
    {
      "evidence_id": "uuid",
      "type": "UrbanHeatEvidence",
      "source": "fortyguard/heatmap",
      "spatial_scope": {},
      "temporal_scope": {},
      "content_hash": "sha256:..."
    }
  ]
}
```

### 2.6 Integrity Manifest

```json
{
  "integrity_manifest": {
    "package_hash": "sha256:...",
    "component_hashes": {
      "original_analysis_request": "sha256:...",
      "provider_executions": "sha256:...",
      "normalized_evidence": "sha256:...",
      "expected_analysis": "sha256:..."
    },
    "verification_method": "SHA-256",
    "verified_at": "ISO 8601"
  }
}
```

---

## 3. Hashing/Integrity Behavior

### 3.1 Hashing Algorithm

**Algorithm:** SHA-256

**Scope:** All package components

### 3.2 Integrity Verification

1. Compute hash of each component
2. Compute package hash from component hashes
3. Compare with stored integrity manifest
4. If mismatch: package is corrupted

### 3.3 Corruption Handling

If integrity verification fails:
1. Do not use the package
2. Report "Package integrity verification failed"
3. Fall back to next available replay package
4. Never silently fabricate data

---

## 4. Fixture Versioning

### 4.1 Version Format

`MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking change to fixture format
- **MINOR:** New fields added (backward compatible)
- **PATCH:** Bug fixes, content updates

### 4.2 Compatibility

- Packages with same MAJOR version are compatible
- Packages with different MAJOR versions require migration

---

## 5. Allowable Redaction

### 5.1 What Can Be Redacted

- API keys (must be redacted)
- Personal identifiers (if present)
- Internal system paths

### 5.2 What Cannot Be Redacted

- Source timestamps
- Spatial coordinates
- Provider identities
- Evidence content
- Provenance chains

---

## 6. Secrets Prohibition

### 6.1 Prohibited Content

The following must NEVER appear in replay packages:

- API keys
- Authentication tokens
- Passwords
- Internal credentials
- Private keys

### 6.2 Verification

Replay packages must be scanned for:
- Pattern matches (API key formats)
- Base64-encoded secrets
- Environment variable references

---

## 7. Deterministic Replay Requirements

### 7.1 Invariants

- Same package produces same analysis output
- No external API calls during replay
- No time-dependent components
- No random components

### 7.2 Allowable Variance

| Component | Allowable Variance |
|-----------|-------------------|
| Timestamps | None (use capture timestamps) |
| Floating point | plus/minus 0.0001 |
| Integer values | None |
| String values | None |
| Array order | None |
| Object keys | None |

### 7.3 Non-Allowable Variance

- Different priority rankings
- Different intervention recommendations
- Different claim support status
- Missing evidence
- Extra evidence

---

## 8. Synthetic Fixtures

### 8.1 Classification

Synthetic fixtures must be explicitly classified as:
- type: "synthetic"
- purpose: "negative_test" or "boundary_test" or "unit_test"
- not_real_execution: true

### 8.2 Prohibition

Synthetic fixtures must NOT:
- Masquerade as captured real evidence
- Appear in replay packages
- Be used for provenance verification
- Be used for integration tests

---

## 9. Schema Incompatibility

### 9.1 Version Mismatch

If schema version does not match:
1. Attempt automatic migration if MINOR version difference
2. Report "Schema version mismatch" if MAJOR version difference
3. Do not silently adapt

---

*Specification complete. Testable by QA-Pilot.*
