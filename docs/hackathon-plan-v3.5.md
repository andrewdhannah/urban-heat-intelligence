# Urban Heat Intelligence — Execution Plan v3.5

**Version:** 3.5.0
**Date:** 2026-08-26
**Supersedes:** v3.4 (hackathon-plan-v3.4.md — preserved as expansion plan)
**Type:** Convergence update — reconciles planned intent with implemented reality

---

## 1. Why v3.5 Exists

v3.4 defined the expansion. Implementation moved ahead of parts of the plan. This update reconciles what was planned with what S3 actually delivered and what remains.

v3.4 is preserved as the expansion reference. v3.5 is the execution guide.

---

## 2. Convergence: v3.4 Intent vs. Actual State

| v3.4 Area | Actual State | Disposition |
|-----------|-------------|-------------|
| S3A Multi-source evidence | Top-3 + FortyGuard + NWS implemented | PARTIAL COMPLETE |
| Phoenix GIS | Preflight deferred | OPTIONAL / unresolved |
| NOAA | Deferred | OPTIONAL / unresolved |
| News/human-interest | Not yet integrated | STILL VALUABLE |
| S3B Urban Heat Brief | Specification exists, product implementation not yet complete | HIGH-VALUE REMAINING |
| S3C Deployment | Render-ready, not publicly deployed | REQUIRED / incomplete |
| S3D Teaching/docs | Extensive teaching set created | SUBSTANTIALLY COMPLETE |
| S3E QA-Pilot | Not yet run against frozen deployed product | REQUIRED / pending |

---

## 3. What v3.5 Incorporates from Implementation

Implementation discovered qualification concerns that v3.4 did not anticipate. v3.5 incorporates them:

| Concern | Source | v3.5 Action |
|---------|--------|-------------|
| NWS provenance / Replay behavior for NWS | S3A implementation | Closeout in S3A.1 |
| Near-tie semantics (candidates with close scores) | S3A implementation | Closeout in S3A.1 |
| Optional human-interest/news context | Owner directive | Include in S3A.1 |
| Content safety review | S3C hardening | Include in S3C |
| Mode validation across full flow | S3C hardening | Include in S3C |
| Public error handling (404, 500, provider down) | S3C hardening | Include in S3C |

---

## 4. Remaining Path

### S3A.1 — Multi-Source Closeout

**Goal:** Complete the multi-source evidence integration that S3A started.

| Work Item | Detail | Priority |
|-----------|--------|----------|
| NWS provenance | Ensure NWS data carries full evidence receipt (source, tool, timestamp, mode) | REQUIRED |
| NWS Replay behavior | Define how NWS fixtures work in Replay mode | REQUIRED |
| Near-tie semantics | When two candidates have close scores, define how ranking handles ties | REQUIRED |
| Optional human-interest/news context | Integrate local news as contextual evidence (never measurement) | VALUABLE |
| Phoenix GIS | Preflight investigation — is this achievable within hackathon scope? | DEFERRED/OPTIONAL |
| NOAA | Preflight investigation — is this achievable within hackathon scope? | DEFERRED/OPTIONAL |

**Exit gate:** All REQUIRED items complete. Decision on OPTIONAL items documented.

---

### S3B — Urban Heat Brief

**Goal:** Implement the first-class narrative brief output specified in BRIEF-SPEC.md.

| Work Item | Detail | Priority |
|-----------|--------|----------|
| Real-source narrative composition | Agent composes brief from actual evidence context | REQUIRED |
| Source-by-source attribution | Every sentence traces to evidence receipt | REQUIRED |
| Conditional sections | Sections present only if source available; absent if not | REQUIRED |
| Minimum brief | FortyGuard-only brief when all other sources unavailable | REQUIRED |
| Human-readable presentation | Weather-news-report format per BRIEF-SPEC.md | REQUIRED |
| Brief export | Plain text and markdown export | VALUABLE |

**Exit gate:** Brief generated from real sources. Every sentence attributable. 0 unsupported claims.

---

### S3C — Harden + Deploy

**Goal:** Production-ready public deployment.

| Work Item | Detail | Priority |
|-----------|--------|----------|
| Content safety review | No offensive content in defaults, fixtures, or output | REQUIRED |
| Mode validation | LIVE/REPLAY labels correct across full flow | REQUIRED |
| Public error handling | Graceful degradation for provider down, stale data, malformed response | REQUIRED |
| Render deployment | Public URL working | REQUIRED |
| Public browser smoke | Chrome, Firefox, Safari — basic flow works | REQUIRED |
| Security review | API key not exposed, no injection vectors | REQUIRED |
| Performance | Response time acceptable for demo | REQUIRED |

**Exit gate:** Public URL live. Basic flow works in 3 browsers. No security issues.

---

### S3D — Documentation Freeze

**Goal:** Reconcile all documentation to implemented truth.

| Work Item | Detail | Priority |
|-----------|--------|----------|
| Reconcile teaching docs | Update teaching docs to match actual implementation (not planned intent) | REQUIRED |
| Architecture doc | Update ARCHITECTURE.md to v3.5 | REQUIRED |
| Data sources doc | Update DATA-SOURCES.md to reflect actually integrated sources | REQUIRED |
| Provenance model | Update PROVENANCE-MODEL.md to match actual evidence chain | REQUIRED |
| README | Final update — actual features, actual commands, actual deployment | REQUIRED |
| Demo scenario | Update DEMO-SCENARIO.md to match actual UI flow | REQUIRED |
| hackathon-plan-v3.4.md | Preserve as historical reference (superseded by v3.5) | DONE |

**Exit gate:** Every doc matches implemented truth. No planned-intent-as-current-state.

---

### S3E — QA-Pilot Full Qualification

**Goal:** Independent qualification of the frozen, deployed product.

| Work Item | Detail | Priority |
|-----------|--------|----------|
| Fresh context | QA-Pilot starts from zero — no carryover from build sessions | REQUIRED |
| Public app | Qualify against the live Render deployment | REQUIRED |
| Repository | Qualify against the actual repo contents | REQUIRED |
| Teaching docs as QA inputs | QA-Pilot consumes 7 teaching docs to reconstruct the product | REQUIRED |
| 6 qualification areas | Analytical correctness, provenance, mode, UX/browser, resilience, reproducibility | REQUIRED |
| Negative scenarios | Multi-source failure, stale data, conflicting sources, mixed provenance | REQUIRED |
| User-guide generation | QA-Pilot produces USER-GUIDE.md, QUICKSTART.md, UNDERSTANDING-EVIDENCE.md | REQUIRED |
| User-guide validation | QA-Pilot follows its own Quick Start against the public product | REQUIRED |
| Final QA report | Complete qualification results | REQUIRED |

**Teaching-docs-as-QA-inputs test:**

The 7 teaching documents (PRODUCT, DECISION-FLOW, LIVE-REPLAY, DATA-SOURCES, EVIDENCE-PROVENANCE, USER-JOURNEYS, FAILURE-STATES) become QA inputs. QA-Pilot must:

1. Consume the teaching docs without reading code
2. Reconstruct understanding of the product from teaching docs alone
3. Produce user documentation (USER-GUIDE.md, QUICKSTART.md, UNDERSTANDING-EVIDENCE.md)
4. Follow its own Quick Start against the public deployment
5. Determine whether its documentation is correct

**Proof obligation:** Can an independent context consume governed teaching material, produce human documentation, and then successfully use that documentation to operate the actual system?

If yes, that is meaningful qualification rather than merely "AI wrote a manual."

**Exit gate:** All 6 areas qualified. User guide validated. Owner acceptance.

---

### S3 ACCEPT / SEAL

**Goal:** Owner accepts the qualified product.

| Gate | Requirement |
|------|-------------|
| All S3A.1 REQUIRED items complete | NWS provenance, near-tie semantics, Replay behavior |
| S3B brief functional | Real-source narrative, 0 unsupported claims |
| S3C deployed | Public URL, browser smoke, security clean |
| S3D docs reconciled | Every doc matches implementation |
| S3E QA passed | All 6 areas, negative scenarios, user guide validated |
| Owner acceptance | Owner reviews and accepts |

---

### S4 — Submission

**Goal:** Final submission package.

| Work Item | Detail |
|-----------|--------|
| Video production | Per VIDEO-PRODUCTION-STORYBOARD.md |
| ≤500-word submission | Written summary |
| README/release | Final README, tagged release |
| Final certification | Last smoke test on public deployment |
| Submission checklist | All 4 requirements met: live demo, repo, video, summary |

---

## 5. Sequencing

```
S3A.1 (Multi-Source Closeout)
    ↓
S3B (Urban Heat Brief)
    ↓
FEATURE FREEZE
    ↓
S3C (Harden + Deploy)
    ↓
S3D (Documentation Freeze)
    ↓
S3E (QA-Pilot Full Qualification)
    ↓
S3 ACCEPT / SEAL
    ↓
S4 (Submission)
```

**Key invariant:** S3E (QA-Pilot) runs AFTER feature freeze and deployment. No qualifying moving state.

---

## 6. What v3.5 Preserves from v3.4

- Expansion principle: "Expand vertically, not horizontally"
- Decision filter: "Will this make the three-minute demo meaningfully better?"
- Urban Heat Brief specification (BRIEF-SPEC.md)
- 7 teaching documents
- Video production storyboard
- Source hierarchy (FortyGuard primary, others optional)
- Live/Replay separation invariant
- 0 unsupported claims rule
- Sequencing rule: FEATURE FREEZE → QA-Pilot → Accept

---

## 7. What v3.5 Changes from v3.4

- S3A split into S3A.1 (closeout remaining items)
- S3B scoped to actual implementation (not expansion dream)
- S3C adds content safety, mode validation, public error handling
- S3D adds reconciliation step (docs must match implementation, not plan)
- S3E detailed with specific qualification areas and exit gates, including teaching-docs-as-QA-inputs
- Convergence section documents what actually happened
- Video story design distinguished from video production

---

## 8. Video Story Design vs. Production

Empirical evidence from S3 implementation settled the video-planning question:

> **Story thinking should begin as soon as the product thesis stabilizes; production waits until feature freeze.**

| Phase | When | What |
|-------|------|------|
| Video story design | Continuous — begins once core product is stable | Decision filter: "Will this make the demo meaningfully better?" Applied to every S3 work item |
| Video production | Only after feature freeze / QA acceptance | Recording, editing, assembly, export in DaVinci Resolve |

This avoids building features nobody will understand or show, while also avoiding recording a UI that's still changing.

### Video Baseline

```
VIDEO STORY BASELINE:
    docs/demo/VIDEO-PRODUCTION-STORYBOARD.md

VISUAL REFERENCE:
    docs/demo/VIDEO-STORYBOARD-VISUAL.png (5-shot key moments reference)

STATUS:
    FROZEN STORY STRUCTURE

PRODUCTION AUTHORITY:
    S4 only

S3 RESPONSIBILITY:
    preserve demo-worthy product states required by storyboard
```

The storyboard is no longer "ideas for a video." It is a production artifact. Its narrative structure is frozen. The next video artifact should be the final timed production script generated after feature freeze and QA-Pilot qualification.

### Editorial Discipline

The storyboard's central rule survives all the way through final export:

> **AI footage illustrates. Real evidence proves.**

### Evidence-Locked Narration

Before final narration recording, create one evidence-locked narration pass. Every factual sentence in the voiceover tagged internally to:

| Tag | Meaning |
|-----|---------|
| FortyGuard | Claim sourced from FortyGuard data |
| NWS | Claim sourced from NWS |
| product-derived comparison | Claim from agent ranking/scoring logic |
| QA evidence | Claim from qualification results |
| general framing | Non-factual narrative (problem statement, emotional close) |

**Rule:** No line sounds stronger than the source supports.

**Example — correct:** "The agent identifies the strongest candidate locations for comparison."

**Example — forbidden if near-tie:** "The agent identifies the clear highest-priority location."

The final script must reflect near-tie nuance and actual implemented evidence.

### Storyboard Key Shots (Frozen)

| Shot | Time | Purpose |
|------|------|---------|
| Shot 1 | 0:00–0:15 | The problem: Phoenix is hot. Human context. Establishes urgency. |
| Shot 2 | 0:35–0:55 | FortyGuard in action. 367 features, top candidates. Core product proof. |
| Shot 3 | 1:14–1:42 | Multiple real sources. Urban Heat Brief. Data becomes decision-ready. |
| Shot 4 | 2:06–2:29 | Explainability & provenance. Every conclusion connected to evidence. |
| Shot 5 | 2:39–3:00 | Reliable by design. Mode separation. Failure visibility. Closing. |

The Urban Heat Brief (Shot 3, ~1:42–1:54) remains the signature product moment. The QA-Pilot section (~9 seconds) establishes credibility without becoming the subject.

---

## 9. Feature Priority (Remaining Work)

Ordered by demonstration value per remaining hour:

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | Urban Heat Brief | Most important v3.4 element not yet in product. Transforms technically strong demo into decision-support product. |
| 2 | NWS provenance correctness | Multi-source evidence is the core innovation. NWS must carry full provenance. |
| 3 | Human-interest/news context | If easy and attributable — adds the weather-news-report dimension. |
| 4 | Deployment | Public URL required for submission. |
| 5 | QA-Pilot + user guide | Independent qualification of the finished product. |
| 6 | Phoenix GIS | Only if an authoritative dataset becomes very easy to consume. |
| 7 | NOAA | Only if historical context can be added very cheaply. |

**The product is already technically deeper than most hackathon entries need to be. The next improvement is coherence.**

---

## 10. Convergence Principle

v3.5 is not "building features." It is converging product, provenance, deployment, documentation, and QA around the features we've chosen.

The expansion is done. The remaining path is convergence.

---

## 11. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| NWS Replay fixtures not recorded | Medium | Medium | Record fixtures during S3A.1 |
| Near-tie semantics ambiguous | Low | Medium | Define deterministic rule before S3B |
| Render deployment issues | Low | High | Test early in S3C |
| QA-Pilot time overrun | Low | High | Feature freeze gate prevents qualifying moving state |
| Video recording delays | Medium | Medium | Storyboard ready; record after S3C deployment |
| GIS/NOAA integration scope creep | Medium | Low | Marked OPTIONAL — defer if not achievable |

---

*This plan supersedes v3.4 for execution purposes. v3.4 is preserved as the expansion reference.*
