# Pitch Structure

## One-Liner (for submission form)

> An evidence-backed heat decision support agent — ask a question about urban heat in natural language, get an answer built from live FortyGuard temperature data, retrieved safety knowledge, and visible reasoning, all wrapped in a receipt showing exactly where every number came from.

## The Problem

Heat kills more people than any other natural disaster globally (UN). But most heat tools just show you a number — a dashboard, a heatmap, a forecast. They don't tell you what it means, what to do about it, or where the data came from. You have to already know the answer to use the tool.

## The Solution

An AI agent that doesn't just show heat data — it explains it. Ask a question in natural language. The agent calls FortyGuard's Temperature API, retrieves relevant knowledge from heat-safety literature, and returns an answer with a full evidence chain: the data source, the retrieved references, and a receipt showing exactly how the answer was constructed.

Every answer carries a receipt.

## How It Works (Five Components)

```
Question → Temperature MCP → Knowledge MCP → Evidence Composer → Receipt → Answer
```

1. **Temperature MCP**: Calls FortyGuard's API for live observations (2m resolution)
2. **Knowledge MCP**: Retrieves relevant passages from heat-safety literature (WHO, OSHA, city guidelines)
3. **Evidence Composer**: Combines live data + retrieved knowledge into a grounded answer
4. **Receipt**: Structured record of every source, tool call, and reasoning step
5. **Answer**: Presented to the user with full provenance

**Example**:
- **You ask**: "What's the heat risk for construction workers in Phoenix right now?"
- **Agent retrieves**: FortyGuard live observation (38.7°C) + OSHA Heat Illness Prevention Guide (Section 4.2) + WHO Heat Health Guidance (2025)
- **Agent answers**: "Current temperature is 38.7°C. OSHA guidance discusses additional precautions under these conditions, including water access every 15 minutes and buddy-system monitoring."
- **Receipt shows**: Each source listed with document name, section, and retrieval timestamp

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Temperature MCP | TypeScript server wrapping FortyGuard Temperature API |
| Knowledge MCP | SQLite + sqlite-vec with embedded heat-safety literature |
| Evidence Composer | Combines live data + retrieved passages into grounded answers |
| Receipt | Structured JSON with source attribution and reasoning chain |
| Interface | Chat shell with evidence-card output |

## What Makes This Different

- **Every other entry shows data. This one shows how the answer was built.**
- Evidence receipts are visible, not hidden — judges see the provenance chain
- Positions as "evidence-backed decision support" not "safety advice" — grounded in retrieved material, not generating novel policy
- Conversational interface — judges interact, not just observe
- Five clean components, not a monolith

## Impact

This pattern — live data + retrieved knowledge + evidence receipts — extends across domains:

- **Worker safety**: "Can my crew work outdoors today?" with OSHA guidance attached
- **Utility planning**: "How will heat affect peak demand this week?" with historical patterns
- **Emergency response**: "Which neighborhoods are at highest heat risk?" with WHO thresholds
- **Infrastructure monitoring**: "Will road surfaces sustain this temperature?" with engineering standards
- **Transit operations**: "Should we adjust service for heat conditions?" with agency guidelines

The temperature API becomes one evidence source among many. The architecture scales to any domain where live data meets domain knowledge.

## Submission Track

**Track 01: Resilient Cities & Infrastructure**
"Design cooler, smarter cities using hyperlocal temperature intelligence. Build AI systems that help urban planners, residents, and emergency services navigate heat at a city scale."

Our build aligns directly: an AI agent that helps urban planners and emergency services navigate heat conditions with evidence-backed decision support.

## Team

Solo entry. Built in two weeks on FortyGuard's Temperature API.

## Links

- GitHub: [repo URL]
- Demo: [deployed URL or localhost instructions]
- FortyGuard API: https://www.fortyguard.com/api-pricing
