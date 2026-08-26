# Demo Script — Two-Minute Walkthrough

## Setup

- Pre-seeded data: Phoenix, AZ (primary demo city)
- API key active (or cached data for offline demo)
- Application running locally at `localhost:PORT`

## Demo Flow

### Opening (10 seconds)

> "This is [Project Name] — a heat-safety agent built on FortyGuard's Temperature API. Unlike a dashboard, it reasons over the data and shows its work. Every answer comes with a receipt."

**Screen**: Chat interface, clean and empty. Title bar with project name.

---

### Scenario 1: Basic Query (30 seconds)

**Type**: "What's the heat risk in downtown Phoenix right now?"

**Agent response** (visible on screen):

1. **Thinking**: Shows tool calls being made
   - `get_temperature(lat: 33.4484, lng: -112.0740)`
   - `get_heat_index(lat: 33.4484, lng: -112.0740)`

2. **Card output**:
   - **Answer**: "Downtown Phoenix is currently at 42.3°C (108.1°F) with a heat index of 48.2°C — classified as **Extreme Danger**. Outdoor activity should be avoided during peak hours."
   - **Sources**: FortyGuard Temperature API, timestamp, 2m resolution
   - **Reasoning**: "Heat index calculated using temperature, humidity (35%), and wind speed (8 km/h). Classification follows the NWS heat index chart."
   - **Receipt**: tool, source, query_time, confidence: high

**PAUSE HERE** (5 seconds): Let the judge read the receipt. Don't narrate over it. The receipt is the pitch — if it flashes by, you've built the differentiator and then hidden it.

**Narration**: "Notice the receipt at the bottom — the system tells you exactly where this number came from and how it was calculated."

---

### Scenario 2: RAG Integration (30 seconds)

> **CRITICAL**: This is the highest-stakes demo moment. The answer retrieves OSHA and WHO guidance. Frame as "decision support" not "safety advice" — the system surfaces what the guidance says, not what you should do. Before demo day: verify every cited source exists and is accurately attributed. Show the source citations prominently.

**Type**: "What should construction workers know about this heat level?"

**Agent response**:

1. **Thinking**: Shows tool calls
   - `query_evidence("construction worker heat safety extreme danger")`
   - `get_heat_index(lat: 33.4484, lng: -112.0740)`

2. **Card output**:
   - **Answer**: "Current heat index is 48.2°C — Extreme Danger. OSHA guidance discusses additional precautions under these conditions, including water access every 15 minutes, shaded rest areas, and buddy-system monitoring. WHO guidance notes core body temperature monitoring when heat index exceeds 40°C."
   - **Sources** (prominently displayed):
     - FortyGuard Temperature API — live observation, 38.7°C, retrieved 0.3s ago
     - OSHA Heat Illness Prevention Guide — Section 4.2
     - WHO Heat Health Guidance — 2025 publication
   - **Evidence chain**: "Combined live temperature observation with retrieved OSHA and WHO guidance. Sources cited above."
   - **Receipt**: tools: [query_evidence, get_heat_index], sources: [fortyguard_api, osha_guide_section_4_2, who_heat_2025]

**PAUSE HERE** (5 seconds): Let the judge see the source citations. This is the moment where "show vs. explain" becomes real — the judge can see the OSHA and WHO documents listed as sources, not just a temperature number.

**Narration**: "It didn't just look up the temperature — it connected the temperature to real safety guidelines and told you which sources it used."

---

### Scenario 3: Forecast + Recommendation (30 seconds)

**Type**: "When will it be safe to work outdoors in Phoenix today?"

**Agent response**:

1. **Thinking**: Shows tool calls
   - `get_forecast(lat: 33.4484, lng: -112.0740, hours: 24)`

2. **Card output**:
   - **Answer**: "Based on the forecast, outdoor work conditions won't reach 'moderate' heat index levels until after 8 PM tonight. The safest window is 8 PM – 6 AM. Peak danger is 12 PM – 6 PM with heat index above 45°C."
   - **Forecast visualization**: Simple inline chart or timeline showing heat index by hour
   - **Sources**: FortyGuard 24-hour forecast, 2m resolution
   - **Receipt**: tool: get_forecast, source: fortyguard_api, confidence: high

**PAUSE HERE** (3 seconds): Let the forecast timeline register.

**Narration**: "The agent doesn't just report current conditions — it looks ahead and gives actionable guidance."

---

### Scenario 4: City Operations (20 seconds)

> **Why this scenario**: Broadens beyond construction safety to show the agent understands cities — closer to FortyGuard's actual market (governments, utilities, urban systems).

**Type**: "Which neighborhood in Phoenix should receive cooling intervention priority today?"

**Agent response**:

1. **Thinking**: Shows tool calls
   - `get_heat_index` for multiple Phoenix neighborhoods
   - `query_evidence("cooling intervention priority urban heat")`

2. **Card output**:
   - **Answer**: "South Phoenix and Maryvale show the highest heat index values (46-48°C) with the least tree canopy coverage. Based on FortyGuard's 2m resolution data, these areas experience 2-3°C higher effective temperatures than adjacent neighborhoods. Municipal guidance suggests prioritizing cooling centers and water distribution in areas exceeding 45°C heat index."
   - **Sources**: FortyGuard multi-location data, municipal heat action plan
   - **Receipt**: tools: [get_heat_index ×4, query_evidence], sources: [fortyguard_api, municipal_guidance]

**Narration**: "The agent doesn't just answer individual queries — it can compare across locations and surface priority actions."

---

### Scenario 4 (Backup): Comparison (20 seconds)

If time is short or judges want to see raw comparison:

**Type**: "How does Phoenix compare to Miami right now?"

**Agent response**:
- **Phoenix**: 48.2°C heat index — Extreme Danger (dry heat)
- **Miami**: 44.1°C heat index — Danger (humidity amplifies feels-like)
- **Key difference**: "Different cities, same threat, different mechanisms."

---

### Closing (10 seconds)

> "Every answer the agent gives carries a receipt — the data source, the reasoning, the confidence. It's not a black box. It's a heat-safety agent that shows its work. Built on FortyGuard's Temperature API with 2-meter resolution."

**Screen**: Final card with receipt visible.

---

## Backup Scenarios (if time permits or judges ask)

### Offline Mode
> "The system caches API responses, so it works even without live API access — useful for demos in areas with poor connectivity."

Show the same queries working with cached data.

### Multi-City
> "Let's check Dubai — FortyGuard's home turf."

Show a query for Dubai, demonstrate global coverage.

---

## What to Have Ready

- [ ] Phoenix data pre-seeded and cached
- [ ] Miami data pre-seeded (for comparison)
- [ ] 5-10 heat-safety documents embedded for RAG
- [ ] Clean chat interface with no debug output
- [ ] Receipt formatting polished (clear hierarchy, not cramped)
- [ ] Backup cached data in case API is slow/down
- [ ] 2-minute timer practiced

## Judge Questions to Prepare For

| Question | Answer |
|----------|--------|
| "How is this different from a dashboard?" | "A dashboard shows data. This explains data. Every answer shows its sources and reasoning." |
| "What's the receipt?" | "A structured record of which tools were called, what data was returned, and why the system concluded what it concluded." |
| "How does the RAG work?" | "We embedded heat-safety documents from WHO, OSHA, and city guidelines. When you ask about worker safety, it retrieves the relevant guidelines and connects them to live temperature data." |
| "What's MCP?" | "Model Context Protocol — a standard way for AI agents to call structured tools. It means the agent knows exactly what data is available and how to get it." |
| "Can this scale beyond a hackathon?" | "The architecture is production-ready. MCP servers are designed to be deployed as services. The evidence receipt pattern works at any scale." |
