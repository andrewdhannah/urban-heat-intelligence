# SPEC-012 Replay Integrity Assessment

**Date:** 2026-08-27
**Authority:** S3D reconciliation

---

## Assessment

SPEC-012 defines replay integrity requirements. This document classifies the current implementation against those requirements.

### Already Satisfied

| Requirement | Evidence |
|-------------|----------|
| Genuine fixture data | Fixtures are real FortyGuard API responses from Aug 25, 2026, stored in `fixtures/fortyguard/` |
| Deterministic replay | Same question + same mode always produces the same result (zero network calls) |
| Zero network calls in Replay | `FortyGuardAdapter(mode="replay")` sets `api_key=None`, never calls any endpoint |
| Provenance visible | Every replay result carries `mode: "replay"`, `observation_time`, fixture reference |
| Fixture files committed to repo | `fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json`, `fixtures/fortyguard/env_params/phoenix-33.4484--112.0740-2026-08-25-14h.json` |
| Fixture hashes computable | SHA-256 hashes can be computed from committed files |

### Cheaply Remediable

| Requirement | Status | Action |
|-------------|--------|--------|
| Content-hash verification at load time | Not implemented | Can add hash check in adapter if desired — low cost |

### Not Implemented / Known Limitation

| Requirement | Status | Classification |
|-------------|--------|---------------|
| Integrity manifest file | No standalone manifest | Hashes are computable from git-tracked files; manifest is optional |
| Replay fixture for NWS | No NWS fixture exists | NWS is excluded from Replay by design — no fixture needed |
| Expected analysis metadata verification | Not implemented | Replay results are deterministic by construction |

### Conclusion

The current replay implementation satisfies the core SPEC-012 obligations: genuine data, deterministic execution, zero network calls, and visible provenance. A standalone integrity manifest is cheaply addable but not required for qualification. NWS exclusion from Replay is by design, not a gap.
