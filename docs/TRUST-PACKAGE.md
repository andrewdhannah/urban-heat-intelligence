# Trust Package

An export from the construction record, not a separate workstream.

**Purpose**: Demonstrate the application is production-minded, not just a prototype.

**How it works**: LINK naturally produces evidence during construction — decisions, tests, provenance, security reviews. The Trust Package is formatting that evidence into documents, not writing new content.

**If LINK cannot produce these artifacts from the construction record**, that itself is useful validation information. Format what exists, note what's missing, move on.

**Audience**: Hackathon judges (closing-slide evidence of engineering quality) + future-facing record of build quality.

---

## Document Set

```
/docs
  README.md              ← already exists
  ARCHITECTURE.md        ← already exists
  PRIVACY.md             ← export from construction record
  SECURITY.md            ← export from construction record
  ACCESSIBILITY.md       ← export from construction record
  TEST-REPORT.md         ← export from test results
  API-PROVENANCE.md      ← export from ingestion provenance
  DEMO-SCRIPT.md         ← already exists
```

---

## PRIVACY.md

**Length**: ~20 lines. Factual, not legal.

**Contents**:
- What data the application collects (API queries, user inputs)
- What data is stored locally (cached API responses, no PII)
- What data leaves the device ( FortyGuard API calls only)
- No user accounts, no analytics, no tracking
- Privacy-relevant design decisions

**Example structure**:
```markdown
# Privacy

## Data Collection
This application queries the FortyGuard Temperature API for temperature
data. No personally identifiable information is collected or stored.

## Local Storage
Temperature data is cached locally in SQLite for demo reliability.
No user data is stored.

## External Calls
Only calls to api.fortyguard.com for temperature data.
No third-party analytics, tracking, or telemetry.

## Design Decisions
- No user accounts required
- No cookies
- No local storage of user inputs beyond the session
```

---

## SECURITY.md

**Length**: ~30 lines. Factual assessment, not a penetration test.

**Contents**:
- Dependency audit summary (npm audit results)
- API key handling (environment variable, not committed)
- Input validation (lat/lng bounds, query sanitization)
- No authentication required (demo application)
- Known limitations (local-only, no HTTPS needed for demo)

**Example structure**:
```markdown
# Security Assessment

## Dependencies
- Total: X packages
- Vulnerabilities: 0 critical, 0 high, X medium, X low
- Audit date: [date]

## API Key Management
- Stored in environment variable, not in source code
- Not logged or exposed in client-side code

## Input Validation
- Latitude: validated to -90 to 90
- Longitude: validated to -180 to 180
- All API inputs sanitized before use

## Known Limitations
- Local-only application, no HTTPS required
- No authentication (single-user demo)
- No rate limiting implemented (hackathon scope)
```

---

## ACCESSIBILITY.md

**Length**: ~20 lines. What was checked, what passes, what's known-limited.

**Contents**:
- Keyboard navigation status
- Screen reader compatibility
- Color contrast compliance
- Known accessibility limitations

**Example structure**:
```markdown
# Accessibility

## Status
- Keyboard navigation: ✓ chat input, map controls
- Screen reader labels: ✓ on interactive elements
- Color contrast: ✓ meets WCAG AA for text
- Focus indicators: ✓ visible on all interactive elements

## Known Limitations
- Heat overlay does not have text equivalent (visual data)
- Map is not fully keyboard-navigable (Leaflet limitation)
- No audio cues (visual-only interface)
```

---

## TEST-REPORT.md

**Length**: ~30 lines. Summary of what was tested and results.

**Contents**:
- Test suite summary (count, pass/fail)
- Key scenarios covered
- Edge cases tested
- Known gaps

**Example structure**:
```markdown
# Test Report

## Summary
- Total tests: X
- Passing: X
- Failing: 0

## Coverage
- MCP tools: all 4 tools tested
- DB layer: cache read/write, RAG search
- Evidence receipts: schema validation for all tools
- Chat interface: message send/receive, card rendering

## Edge Cases
- API timeout: graceful fallback to cached data
- Empty RAG results: agent responds without evidence chain
- Invalid coordinates: input validation rejects out-of-bounds

## Known Gaps
- No load testing (single-user demo)
- No concurrent session testing
```

---

## API-PROVENANCE.md

**Length**: ~20 lines. Documents every external data source.

**Contents**:
- FortyGuard API endpoints used
- Data returned by each endpoint
- Caching strategy
- Attribution requirements

**Example structure**:
```markdown
# API Provenance

## External Data Sources

### FortyGuard Temperature API
- Endpoint: [exact endpoint URLs]
- Data: Temperature at 2m resolution, heat index, forecast
- Auth: API key via environment variable
- Caching: Responses cached in SQLite, refreshed on query
- Attribution: "Temperature data provided by FortyGuard"

### Embedded Knowledge Base
- Source: OSHA Heat Illness Prevention Guide
- Source: WHO Heat Health Guidance (2025)
- Source: City of Phoenix Heat Action Plan
- Storage: SQLite with sqlite-vec embeddings
- Attribution: Each source cited in evidence receipts
```

---

## When to Write These

**Day 12-13** in the sprint plan. Not before — the application needs to exist first. Not after — too close to submission.

**Order of priority** (if time runs short):
1. TEST-REPORT.md — judges care about working software
2. SECURITY.md — FortyGuard targets governments/utilities; security matters
3. PRIVACY.md — short, easy to write, important for the audience
4. API-PROVENANCE.md — documents the data sources
5. ACCESSIBILITY.md — good-to-have, not critical for hackathon
