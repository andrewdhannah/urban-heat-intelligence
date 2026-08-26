# Librarian Release Candidate Plan

**Goal**: Get the Librarian to release candidate quality before the FortyGuard hackathon starts (August 18, 2026).

**Current State**:
- 532 total sprints, 473 sealed
- V1 already released (sealed #162)
- Current active sprint: SEMANTIC-OWNER-DECISION-RECORD-1
- Evidence Intelligence: Complete
- Semantic Architecture Foundation: Complete
- Semantic Application Layer: In progress

**What "RC Quality" Means for the Hackathon**:
The hackathon proves the system works by building a real application with it. The RC needs to be:
- Stable enough to build with
- Testable enough to validate
- Documented enough to use
- Governance sound enough to demonstrate

---

##13-Day RC Plan (August 5–17)

### Phase 1: Stabilize (Days 1-4)

**Focus**: Complete current epics, seal pending work.

- [ ] Complete SEMANTIC-OWNER-DECISION-RECORD-1 (current sprint)
- [ ] Seal any pending_owner_review items (2 items)
- [ ] Complete EPIC-LIBRARIAN-SEMANTIC-APPLICATION-LAYER-1
- [ ] Run full test suite, fix any failures
- [ ] Validate governance chain is sound

**Success Criteria**: All active epics sealed, test suite passing.

### Phase 2: Harden (Days 5-8)

**Focus**: Ensure the system is buildable-with, not just demo-able.

- [ ] Validate MCP tools are functional (librarian_search, librarian_query, etc.)
- [ ] Validate evidence intelligence pipeline works end-to-end
- [ ] Validate semantic index is operational
- [ ] Validate governance receipts are generated correctly
- [ ] Run validation harness, fix any failures

**Success Criteria**: Core capabilities verified working.

### Phase 3: Package (Days 9-12)

**Focus**: Make the system usable for the hackathon build.

- [ ] Ensure startup sequence works reliably
- [ ] Ensure project selection works
- [ ] Ensure work packet flow works
- [ ] Document any known limitations
- [ ] Create hackathon-specific shortcuts (if needed)

**Success Criteria**: Can start a new project and build with the system.

### Phase 4: Validate (Days 13-17)

**Focus**: Final validation before hackathon.

- [ ] Run full validation harness
- [ ] Test the FortyGuard project setup (create project, initialize, start building)
- [ ] Verify all governance artifacts are in place
- [ ] Document the build workflow for the hackathon

**Success Criteria**: Ready to build on August 18th.

---

## What the Hackathon Proves

The hackathon is not a demo of the Librarian. It's a field trial:

| Question | How the Hackathon Answers It |
|----------|------------------------------|
| Can the system coordinate a real build? | Build the FortyGuard agent using the Librarian |
| Does governance slow things down? | Compare build speed to ungoverned development |
| Do evidence receipts work in practice? | Generate receipts during the build |
| Can the system handle external constraints? | FortyGuard API, real deadline, external evaluation |
| Is the construction methodology sound? | Retrospective analysis after submission |

---

## Success Criteria for August 17th

On the morning of August 17th, you should have:

- [ ] All active epics sealed
- [ ] Test suite passing
- [ ] Core MCP tools functional
- [ ] Evidence intelligence working
- [ ] Semantic index operational
- [ ] Startup sequence reliable
- [ ] Project selection working
- [ ] Work packet flow working
- [ ] Validation harness passing
- [ ] Known limitations documented

If you have all of these, the system is ready to build with on August 18th.

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| Current sprint takes too long | Focus on minimum viable completion, defer polish |
| Test suite has failures | Prioritize core tests, defer edge cases |
| MCP tools not functional | Use file-based workflow as fallback |
| Governance too heavy for hackathon | Use advisory-only mode, defer strict enforcement |
| Startup sequence unreliable | Create manual shortcut for project setup |

---

## What NOT to Do Before the Hackathon

- Do not add new features
- Do not refactor existing code
- Do not change governance rules
- Do not update documentation (unless critical)
- Do not optimize performance

The goal is stability, not perfection. The hackathon will reveal what actually needs improvement.
