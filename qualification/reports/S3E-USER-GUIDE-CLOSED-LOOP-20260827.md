# S3E User Guide Closed-Loop Report — Urban Heat Intelligence

**Producer:** QA-Pilot
**Date:** 2026-08-27
**Status:** PASS — awaiting Owner acceptance

---

## PROCEDURE

### Generation Boundary

Documents generated from the 7 teaching documents ONLY:
- UHI-PRODUCT-TEACHING-001
- UHI-DECISION-FLOW-TEACHING-001
- UHI-LIVE-REPLAY-TEACHING-001
- UHI-DATA-SOURCES-TEACHING-001
- UHI-EVIDENCE-PROVENANCE-TEACHING-001
- UHI-USER-JOURNEYS-TEACHING-001
- UHI-FAILURE-STATES-TEACHING-001

No implementation code was read during documentation generation.

### Documents Generated

| Document | Path |
|----------|------|
| User Guide | `docs/user-guide/USER-GUIDE.md` |
| Quick Start | `docs/user-guide/QUICKSTART.md` |
| Evidence Guide | `docs/user-guide/UNDERSTANDING-YOUR-EVIDENCE.md` |

### Procedure

1. Read all 7 teaching documents
2. Generate candidate USER-GUIDE.md, QUICKSTART.md, UNDERSTANDING-YOUR-EVIDENCE.md
3. Use candidate Quick Start to verify product reproduction
4. Use USER-GUIDE.md to operate the public product
5. Use UNDERSTANDING-YOUR-EVIDENCE.md to interpret evidence/provenance
6. Record every discrepancy
7. Correct documentation where product is correct and teaching material supports correction
8. Re-verify after correction

---

## VERIFICATION

### Public Application Exercised

- URL: `https://urban-heat-intelligence.onrender.com/`
- Mode: Replay (auto-runs on load)
- Features verified: map, 367 polygons, 3 ranked candidates, near-tie disclosure, Urban Heat Brief, evidence chain, mode toggle

### Clean Reproduction Exercised

- Python 3.14.4, no external dependencies
- `python3 app/server.py` starts successfully
- Replay works without credential
- Fixtures load from `fixtures/fortyguard/`

---

## VERIFICATION CHECKS (17)

| # | Check | Source Doc | Expected | Observed | Result |
|---|-------|-----------|----------|----------|--------|
| 1 | Replay mode works out of box | USER-GUIDE | mode=replay | mode=replay | PASS |
| 2 | No credentials for replay | USER-GUIDE | no FORTYGUARD_API_KEY needed | tested without | PASS |
| 3 | Observation time Aug 25 | USER-GUIDE | 2026-08-25 in obs_time | 2026-08-25T14:00:00-07:00 | PASS |
| 4 | 3 ranked candidates | USER-GUIDE | 3 candidates | 3 candidates | PASS |
| 5 | Brief exists | USER-GUIDE | brief card rendered | brief card rendered | PASS |
| 6 | Near-tie threshold < 0.1°C | USER-GUIDE | spread < 0.1 | 0.0004 < 0.1 | PASS |
| 7 | NWS excluded from replay | USER-GUIDE | excluded_from_replay | excluded_from_replay | PASS |
| 8 | Evidence chain expandable | USER-GUIDE | chain nodes > 0 | 16 nodes | PASS |
| 9 | Server imports OK | QUICKSTART | import succeeds | import succeeds | PASS |
| 10 | Python 3.10+ required | QUICKSTART | sys.version >= 3.10 | 3.14 >= 3.10 | PASS |
| 11 | No pip install needed | QUICKSTART | requirements.txt empty | comment-only | PASS |
| 12 | Replay auto-runs on load | QUICKSTART | index.html init calls runQuery | confirmed | PASS |
| 13 | 0 unsupported claims | EVIDENCE | count=0 | count=0 | PASS |
| 14 | 7 brief claims | EVIDENCE | count=7 | count=7 | PASS |
| 15 | All claims have source_provider | EVIDENCE | all=true | all=true | PASS |
| 16 | All claims have mode | EVIDENCE | all=true | all=true | PASS |
| 17 | NWS used_in_decision=False | EVIDENCE | all NWS claims false | all false | PASS |

**All 17 checks: PASS**

---

## DOCUMENTATION DISCREPANCIES

### Discrepancy 1 (Found During First Pass)

**Area:** Claim taxonomy presentation in UNDERSTANDING-YOUR-EVIDENCE.md

**Issue:** Documentation used product aliases instead of normative SPEC-011 class names.

**Correction:** Updated to normative SPEC-011 class names with aliases as secondary labels.

**Product behavior changed:** False.

### Discrepancy 2 (Found During Owner Review — First Remediation)

**Area:** PROVENANCE-MODEL.md and QUICKSTART.md — evidence persistence architecture

**Issue:** PROVENANCE-MODEL.md claimed "Append-only SQLite table" with `CREATE TABLE evidence_log` schema. QUICKSTART.md claimed "SQLite with sqlite-vec for evidence and embeddings." Actual implementation uses in-memory Python list returned as JSON.

**Root cause:** Teaching-doc consistency ≠ teaching-doc truth. QA-Pilot verified documentation against documentation, not against frozen implementation.

**Correction:** PROVENANCE-MODEL.md replaced SQLite section with in-memory evidence chain model. QUICKSTART.md removed SQLite claim.

**Product behavior changed:** False.

### Discrepancy 3 (Found During Owner Review — Second Remediation)

**Area:** UNDERSTANDING-YOUR-EVIDENCE.md — residual receipt-schema terminology

**Issue:** After the first remediation, UNDERSTANDING-YOUR-EVIDENCE.md still used "evidence receipt" terminology and described receipt-schema fields (`receipt_id`, `cached`, `confidence`, `query_time`) that do not exist in the frozen implementation. The frozen implementation's evidence chain nodes contain only `step`, `data`, `timestamp`. The brief claim envelope contains `claim_id`, `text`, `source_provider`, `source_type`, `evidence_nodes`, `mode`, `observation_time`, `retrieved_at`, `effective_period`, `used_in_decision`, `governing_threshold_celsius`.

**Root cause:** Partial remediation ≠ obligation closure. The first remediation corrected PROVENANCE-MODEL.md and QUICKSTART.md but did not fully propagate to UNDERSTANDING-YOUR-EVIDENCE.md.

**Correction:** Replaced "evidence receipt" with "evidence chain node" throughout. Added Brief Claim Provenance section documenting the claim envelope structure. Updated QUICKSTART.md "evidence receipt" to "evidence chain node" for consistency.

**Product behavior changed:** False.

**Lesson:** teaching-doc consistency ≠ teaching-doc truth, AND partial remediation ≠ obligation closure. Implementation-aware verification must check claims against frozen source code, not only against other documentation.

---

## FINAL STATE

| Metric | Value |
|--------|-------|
| Final discrepancies | 0 (after 3 remediation passes) |
| Product defects found | 0 |
| Documentation corrections | 3 (taxonomy terminology + provenance architecture + receipt terminology) |
| Product behavior changed | false |
| Implementation-aware revalidation | PASS |
| **Final result** | **PASS (after remediation)** |

**History:**
1. Initial closed-loop: PASS with 0 discrepancies (but missed stale claims)
2. Owner review #1: Found stale SQLite provenance claim → first remediation
3. Owner review #2: Found residual receipt-schema terminology → second remediation
4. Implementation-aware revalidation: PASS — evidence chain nodes verified as step/data/timestamp, brief claims verified, zero SQLite in codebase

**Root lessons:** teaching-doc consistency ≠ teaching-doc truth; partial remediation ≠ obligation closure.

---

*This report preserves the closed-loop proof as its own inspectable artifact. The candidate user documentation accurately describes the actual product behavior.*
