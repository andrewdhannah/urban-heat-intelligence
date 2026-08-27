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

### Discrepancy 1 (Initial — Found During First Pass)

**Area:** Claim taxonomy presentation in UNDERSTANDING-YOUR-EVIDENCE.md

**Issue:** Documentation used product aliases (DERIVED_CALCULATION, COMPARATIVE_STATEMENT, etc.) instead of normative SPEC-011 class names (DERIVED_FINDING, PRIORITY_CLASSIFICATION, etc.).

**Root cause:** Teaching documents use product aliases; normative specification uses different class names. Documentation inherited the aliases.

**Correction made:** Updated UNDERSTANDING-YOUR-EVIDENCE.md claim taxonomy table to use normative SPEC-011 class names with product aliases as secondary labels.

**Product behavior changed:** False.

### Discrepancy 2 (Found During Owner Review)

**Area:** PROVENANCE-MODEL.md and QUICKSTART.md — evidence persistence architecture

**Issue:** PROVENANCE-MODEL.md claimed "Append-only SQLite table" with a `CREATE TABLE evidence_log` schema. QUICKSTART.md claimed "SQLite with sqlite-vec for evidence and embeddings" and "every tool call produces an evidence receipt stored in SQLite." The actual implementation uses an in-memory Python list (`self.evidence_chain = []` in `controller.py`) returned as JSON in the API response. Zero SQLite usage exists in the codebase.

**Root cause:** Teaching docs inherited the SQLite claim from earlier architectural planning. QA-Pilot's closed-loop test verified documentation against documentation (teaching docs), not against the frozen implementation. The test correctly identified that the teaching docs and user-guide docs were consistent — but both were stale relative to the actual code.

**Classification:** Documentation-governance defect. Teaching-doc consistency ≠ teaching-doc truth.

**Correction made:**
- `docs/data/PROVENANCE-MODEL.md`: Replaced "Evidence Log" SQLite section with "Evidence Chain" describing the in-memory list + JSON API response model. Updated "Why?" Panel section to reference the evidence chain rather than "evidence log."
- `docs/user-guide/QUICKSTART.md`: Removed "SQLite with sqlite-vec" claim. Replaced with accurate evidence chain description. Restored Dashboard and Architecture lines that were accidentally removed.

**Product behavior changed:** False.

**Lesson:** Future closed-loop tests must verify architectural claims (persistence model, dependencies, data flow) against the actual frozen implementation, not only against the teaching documents.

---

## FINAL STATE

| Metric | Value |
|--------|-------|
| Final discrepancies | 0 (after remediation) |
| Product defects found | 0 |
| Documentation corrections | 2 (taxonomy terminology + provenance architecture) |
| Product behavior changed | false |
| **Final result** | **PASS (after remediation)** |

**Note:** The initial closed-loop test reported PASS with zero discrepancies. Owner review identified a documentation-governance defect (stale SQLite provenance claim) that the test missed. This was remediated in a subsequent documentation-only commit. The defect was in documentation accuracy, not in product behavior.

---

*This report preserves the closed-loop proof as its own inspectable artifact. The candidate user documentation accurately describes the actual product behavior.*
