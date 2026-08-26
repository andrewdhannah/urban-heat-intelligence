# Competition Analysis & Differentiation

## What FortyGuard Already Knows Works

From the London "Health in Climate AI Hackathon" (June 2026), teams built:

- **Heat-health early-warning tools** — alerts when heat thresholds are crossed
- **Heat exposure mapping across vulnerable communities** — GIS-style heat overlays
- **Cooling and shade-access planning** — where to put trees, shelters
- **Worker-safety and outdoor-labor applications** — construction, agriculture heat alerts
- **Models connecting ambient temperature to health outcomes** — predictive health risk

These are the expected submissions. Every team with a data scientist will build a variation of one of these.

## What You're Building That's Different

| Typical Hackathon Entry | Your Entry |
|------------------------|-----------|
| Dashboard that shows heat data | Agent that *reasons* over heat data |
| "Here's a heatmap" | "Here's what the heatmap means, and here's why I'm telling you this" |
| Data visualization | Evidence-backed conversation |
| Static output | Receipt-bearing reasoning chain |
| One tool | MCP server with 6 tools + RAG |
| "Trust me, here's the number" | "Here's the number, here's where it came from, here's what it means" |

**The core differentiator**: You're not building a dashboard. You're building an *attestation layer* — a system that doesn't just show data, but shows its work. Every answer comes with a receipt. That's the Librarian pattern applied to climate data.

## Likely Competitor Archetypes

### 1. The Dashboard Builder
- Leaflet/Mapbox heatmap of FortyGuard data
- Some filtering by time/location
- Pretty, but passive — user has to know what to look for
- **Weakness**: No reasoning, no guidance, just data display

### 2. The Predictive Modeler
- Trains a model on FortyGuard data + health/economic data
- Predicts heat-related ER visits, energy demand, etc.
- Impressive technically, but opaque — "the model says X"
- **Weakness**: No explainability, no evidence chain, black box

### 3. The Alert System
- Threshold-based alerts: "Heat index > 40°C in your area"
- Simple, useful, but shallow — no context, no reasoning
- **Weakness**: Binary (alert/no alert), no nuance, no sources

### 4. The Policy Dashboard
- Targets city planners and policymakers
- Shows heat data overlaid with demographics, infrastructure
- **Weakness**: Passive tool, requires domain expertise to interpret

### 5. You (The Evidence Agent)
- Conversational interface — ask questions in natural language
- Agent reasons visibly, calls tools, shows its work
- Every answer carries a receipt: data source, timestamp, confidence
- RAG layer connects heat data to real safety guidelines
- **Strength**: Judges can *see* why the system concluded what it concluded

## Your Advantage

### 1. Explainability
Every other entry will show data. Yours will explain data. When a judge asks "how did you arrive at that answer?", every other team will say "the model" or "the API". You'll show a receipt.

### 2. Conversation, Not Dashboard
Judges interact with dashboards passively. They interact with agents actively. A conversation is a better demo than a dashboard because the judge controls the pace and direction.

### 3. Evidence Chain as Feature
This isn't a technical feature buried in the code — it's the visible output. Judges see it without being told to look for it.

### 4. RAG Integration
Connecting FortyGuard's live data to established heat-safety knowledge (WHO, EPA) shows you're not just visualizing data — you're contextualizing it.

### 5. MCP Architecture
MCP (Model Context Protocol) is a recognized standard for agent-tool integration. Building on it shows architectural awareness beyond "I wrapped an API call."

## Risks to This Strategy

| Risk | Mitigation |
|------|-----------|
| Judges don't understand MCP | Explain it in plain language: "structured tools for an AI agent" |
| Evidence chain looks like boilerplate | Make sure each receipt is genuinely different per query |
| Chat interface feels basic | Polish the card design — clean typography, clear hierarchy |
| FortyGuard wants dashboards, not agents | The hackathon says "AI agent" is a track — you're on-brief |

## Judging Criteria Alignment

Based on FortyGuard's hackathon brief and typical hackathon scoring, expect these dimensions:

| Criteria | What They're Looking For | Your Strength |
|----------|------------------------|---------------|
| **Novel use of Temperature API** | Creative application of FortyGuard's data | Agent that reasons over live data + retrieved knowledge — not just displaying it |
| **Technical execution** | Working, polished demo | MCP architecture, SQLite/sqlite-vec, clean chat interface |
| **Practical usefulness** | Could someone actually use this? | Decision support for worker safety, utility planning, emergency response |
| **Presentation quality** | Clear, compelling demo | Evidence cards with visible provenance — the receipt *is* the presentation |
| **Clear differentiation** | Why this instead of other entries? | Every other entry shows data. This one shows how the answer was built. |

**Your governance architecture contributes mainly to the last two.** That's why the demo matters more than the code — judges need to *see* the differentiation, not just hear about it.

## Positioning Statement

> "Most heat tools show you the data. Ours shows you how the answer was built. Every answer carries a receipt — the live data source, the retrieved references, the reasoning. It's evidence-backed decision support, not a dashboard. You don't need to trust the system; you can verify it."
