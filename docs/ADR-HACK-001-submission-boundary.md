# ADR-HACK-001: FortyGuard Submission Boundary

**Date:** 2026-08-18
**Status:** Accepted
**Source:** FortyGuard Hackathon Participant Handbook (Page 20)
**Last Updated:** 2026-08-26 — IP term evidence levels corrected per Owner directive

---

## Decision

The hackathon submission contains only newly created composition and adapter code. Pre-existing Librarian platform infrastructure remains outside the submission boundary.

### Submitted (Hackathon-Created IP)

```
fortyguard-librarian-demo/
├── dashboard/                    # React + Three.js + CSS
├── addons/
│   ├── web-search/              # New: SearXNG adapter
│   └── fortyguard/             # New: FortyGuard adapter
├── composition/                 # New: Analysis workflow
├── contracts/                   # New: Demo capability contracts
├── fixtures/                    # New: Test data
├── validation/                  # New: Evidence verification
├── docs/                        # New: Documentation
├── run-demo                     # New: Startup script
└── README.md                    # New: Submission docs
```

### Referenced (Pre-Existing Background IP)

```
NOT SUBMITTED:
├── Librarian Core              # Pre-existing
├── Librarian Node              # Pre-existing
├── librarian-sdk               # Pre-existing
├── librarian-vault             # Pre-existing
├── working-bibliography-extension  # Pre-existing
└── Platform Equivalence        # Pre-existing
```

---

## Rationale

### IP Terms (Supported — pending verification of remaining handbook terms)

**Source:** FortyGuard Hackathon Participant Handbook, Page 20
**Term:** "You own what you build."

**Evidence level:** Supported by page-20 language. The following implications are reasonable inferences from "You own what you build" but are NOT individually confirmed by that phrase alone. Remaining handbook terms (pages 17-20) may provide additional confirmation or qualification.

**Implications:**
1. Participant retains ownership of submitted code — **Supported**
2. No IP assignment to FortyGuard — **Supported** (by "You own what you build"; remaining handbook terms not yet confirmed)
3. Pre-existing Librarian IP remains with participant — **Supported**
4. No obligation to expose Core/Node/SDK/Vault source — **Pending verification** (public-repo requirement could interact with submission/IP boundary)
5. Composition layer is owned by participant — **Supported**
6. No license grant to FortyGuard beyond display/demonstration — **Pending verification** (same reason as #4)

### Architectural Justification

1. **Composition, not reconstruction.** The hackathon demonstrates that independently governed capabilities can compose into a useful workflow. This requires a thin composition layer, not rebuilding the platform.

2. **Platform separation.** Librarian Core, Node, SDK, Vault, and Biblio are pre-existing infrastructure. The hackathon project is a new application layer that references these components through stable interfaces.

3. **Defensible boundary.** The submission contains only code written during the hackathon period, plus any new adapters or capabilities created for this project. Pre-existing components are identified as background IP.

4. **Reuse without submission.** The demo can run against pre-existing Librarian components as external dependencies without including their source in the submission repository.

---

## Consequences

### Positive

- Clean IP boundary between hackathon work and platform
- No obligation to expose proprietary infrastructure
- Demonstrates composition over platform (stronger story)
- Pre-existing components remain controlled

### Negative

- Must ensure interfaces are stable enough for external dependency
- Demo setup requires pre-existing Librarian environment
- May need to document dependency requirements

### Risks

- If hackathon rules require all dependencies to be public, may need to adjust
- If rules require self-contained demo, may need to include minimal Librarian runtime

---

## Verification Checklist

- [x] Confirm "you own what you build" applies to all submitted code — **Confirmed** (handbook page 20)
- [x] Confirm submission format (GitHub repo, video, etc.) — **Confirmed** (handbook §11: live demo, public repo, 3-min video, 500-word summary)
- [x] Confirm judging criteria — **Confirmed** (handbook: Impact 40%, Technical 35%, Innovation 15%, Communication 10%)
- [ ] Confirm no requirement to submit source of dependencies — **Pending** (public-repo requirement may interact)
- [ ] Confirm pre-existing IP can be referenced but not submitted — **Pending** (same reason)
- [ ] Confirm no license grant to FortyGuard beyond display/demonstration — **Pending**
- [ ] Confirm no restriction on using other AI/ML tools in submission — **Pending**

---

## Next Steps

1. ~~Verify remaining IP terms from handbook (pages 17-20)~~ — Partially confirmed via full handbook reading (22 screenshots). Submission format and judging criteria confirmed. IP boundary terms pending remaining page review.
2. ~~Document submission format requirements~~ — **Done** (handbook §11: live demo, public repo, 3-min video, 500-word summary)
3. ~~Confirm judging criteria to optimize for~~ — **Done** (Impact 40%, Technical 35%, Innovation 15%, Communication 10%)
4. Finalize dependency declaration approach (pending IP boundary confirmation)
