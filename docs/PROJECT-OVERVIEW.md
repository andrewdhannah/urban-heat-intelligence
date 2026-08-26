# FortyGuard Hackathon 26 — Project Overview

## The Event

- **Organizer**: FortyGuard (temperature-intelligence layer for cities)
- **Dates**: August 18–30, 2026 (two weeks)
- **Format**: Global, virtual, free to enter
- **Tagline**: "Building the World's Temperature AI — What if AI could see heat and solve it?"
- **Registration**: https://www.fortyguard.com/hackathon26
- **Team Size**: Solo or team (max 3)
- **No climate background required**

### Challenge Tracks

**Track 01: Resilient Cities & Infrastructure**
"Design cooler, smarter cities using hyperlocal temperature intelligence. Build AI systems that help urban planners, residents, and emergency services navigate heat at a city scale."

Build examples: Cool Route Planner, Public Asset Heat Audit, Digital Twin Simulation

**Track 02: Future Build** (partially visible on page — check when API key arrives)

You can select one challenge or combine multiple.

### Technologies Encouraged

Temperature API, GIS, Urban AI, Climate Intelligence

### Prizes

- 3rd Place: $1,000
- 1st and 2nd: Not visible on page (likely higher)
- All participants receive certificates
- Top teams receive career opportunities and partner visibility

### Participant Benefits

- Free Temperature API access
- Trial API credits
- Developer Quickstart
- Documentation
- Community Slack
- Technical Support
- Certificate of Completion
- Partner Network Access

## FortyGuard

- Measures heat hyperlocally at 2 meters above ground (where people and infrastructure feel it)
- Hour-by-hour, 2-meter resolution data
- Large Temperature Models are NVIDIA-recognized
- Backed by Microsoft for Startups, Google GovTech, Techstars
- Governments and utilities use their Temperature API to predict extreme heat

## Our Build

**Working Name**: TBD (candidates: Isotherm, Shadecast, Heatline, Swelter, HeatLedger)

**One-liner**: A heat-safety agent that reasons over FortyGuard's hyperlocal temperature data with visible evidence chains — you ask it a question, it shows you the data, the sources, and why it's telling you what it's telling you.

**Track**: AI Agent (primary), with a dashboard/map as the presentation layer

### What We're Building

1. **MCP Server** — TypeScript server wrapping FortyGuard's Temperature API, exposing structured tools for querying temperature data, heat indices, and forecasts
2. **SQLite + sqlite-vec DB** — Local evidence store: cached API responses, heat-safety reference documents, vector embeddings for semantic retrieval
3. **Chat Interface** — Rebuilt from LINK pattern: message in, agent reasons with visible sources, card out. Clean rebuild, not a copy.
4. **Dashboard** — Simple HTML layer showing heat data on a map or timeline

### Transferable Patterns from The Librarian

| Pattern | How It Applies |
|---------|---------------|
| DB-first ordering | Evidence store before API integration |
| Evidence receipts | Every answer comes with a visible reasoning chain |
| Chat-as-presentation-layer | Agent output arrives as presented cards, not raw dumps |
| MCP tool schema | Structured tool definitions for the Temperature API |
| sqlite-vec for RAG | Lightweight vector search without a separate DB service |

---

## Internal Framework: Three Layers

**This section is internal. Do not include in hackathon submission.**

### Layer 1 — The FortyGuard Submission (External Deliverable)

```
Temperature MCP → Knowledge MCP → Evidence Composer → Receipt → Answer
```

Success criteria:
- Uses FortyGuard API meaningfully
- Produces a compelling demo
- Works reliably
- Understandable in 3–5 minutes

Everything else serves this.

### Layer 2 — LINK Internal Construction Validation

Happens automatically from the workflow, not as a parallel activity.

**Do not add**: daily research journals, extra dashboards, separate validation ceremonies.

**Do instead**: After completion, inspect existing artifacts — commits, decisions, receipts, tests, generated documentation, review records.

The question afterward: "What evidence did LINK naturally produce while building this?"

That is much stronger than: "I carefully documented LINK while using LINK." The first is a system property. The second is a manual process.

### Layer 3 — Trust Package (Export, Not Workstream)

The Trust Package is an export from the construction record, not a separate workstream.

**Bad**:
```
Build app + Write security doc + Write privacy doc + Write accessibility doc
```

**Good**:
```
Build app → LINK evidence → export to ARCHITECTURE.md, SECURITY.md, PRIVACY.md, etc.
```

If LINK cannot produce those artifacts from the construction record, that itself is useful validation information. Format what exists, note what's missing, move on.

### The Real Validation

Can a normal project start from zero and naturally accumulate: decisions, provenance, tests, security evidence, accessibility evidence, release confidence?

If yes, that is meaningful. The hackathon is the test. The evidence comes from inspecting what was produced, not from narrating the process live.

### LINK Attribution (Subtle, Not Promotional)

LINK stays invisible to judges. Attribution goes in places that serve as internal records and future-facing provenance, not marketing:

- **Repo metadata**: `package.json` description — "Built with a governed AI-assisted development workflow"
- **Documentation footer**: "Engineering workflow: Constructed and validated using LINK governance practices"
- **Architecture docs**: Small "Development Methodology" section
- **Release artifact metadata**: `"constructionWorkflow": "LINK", "validationStatus": "verified"`

**Do not add**: splash screens, hero sections, demo opening slides, app UI branding. Judges should remember the heat agent, not LINK.

## Team

- Andrew (solo)

## Timeline

Two-week sprint. See `SPRINT-PLAN.md` for breakdown.

## Links

- [FortyGuard Hackathon Page](https://www.fortyguard.com/hackathon26)
- [FortyGuard Temperature API](https://www.fortyguard.com) (check docs for API reference)
