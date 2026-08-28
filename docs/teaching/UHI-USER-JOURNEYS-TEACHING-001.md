# Urban Heat Intelligence — User Journeys Teaching Document

**Document ID:** UHI-USER-JOURNEYS-TEACHING-001
**Purpose:** Enable a fresh agent to understand how different users interact with the product.
**Consumer:** QA-Pilot, documentation generators
**Owner:** urban-heat-intelligence

---

## 1. User Personas

### 1.1 City Planner

**Goal:** Identify where to prioritize cooling intervention funding.
**Expertise:** GIS, urban planning, policy.
**Typical query:** "Which neighborhood should receive cooling intervention priority?"
**Value from product:** Ranked locations with evidence-backed justification and intervention recommendations.

### 1.2 Emergency Manager

**Goal:** Assess current heat risk and activate response protocols.
**Expertise:** Emergency management, NWS products.
**Typical query:** "What's the heat risk in downtown Phoenix right now?"
**Value from product:** Current conditions with official NWS corroboration, rapid decision support.

### 1.3 Journalist / Reporter

**Goal:** Understand and report on heat conditions with accurate data.
**Expertise:** Writing, public communication.
**Typical query:** "What should our audience know about today's heat?"
**Value from product:** Urban Heat Brief — ready-to-publish narrative with attributed sources.

### 1.4 Resident / Community Member

**Goal:** Understand personal heat risk and find cooling resources.
**Expertise:** General public.
**Typical query:** "Is it safe to be outside right now?"
**Value from product:** Plain-language assessment with evidence, cooling centre locations.

### 1.5 Judge / Reviewer (Hackathon)

**Goal:** Evaluate technical execution and innovation.
**Expertise:** Software, AI, data science.
**Typical query:** [Watches demo video]
**Value from product:** Evidence chain, provenance model, multi-source intelligence, governance story.

---

## 2. Journey Maps

### 2.1 City Planner Journey

```
Open app
    ↓
Agent analyzes FortyGuard data (367 thermal features)
    ↓
Agent ranks top-3 priority locations
    ↓
Agent presents the Urban Heat Brief and near-tie interpretation
    ↓
Planner clicks "Inspect evidence +"
    ↓
Planner reviews the evidence chain (FortyGuard; NWS only in LIVE)
    ↓
Planner reads source and mode labels
```

### 2.2 Emergency Manager Journey

```
Open app
    ↓
Query: "What's the heat risk right now?"
    ↓
Agent calls FortyGuard + NWS
    ↓
Agent reports: "Excessive Heat Warning. Four areas above 43°C."
    ↓
Agent identifies highest-risk location
    ↓
Manager clicks "Why?" for evidence
    ↓
Manager notes NWS advisory + FortyGuard temperature
    ↓
Manager activates response protocol
```

### 2.3 Journalist Journey

```
Open app
    ↓
Query: primary Phoenix cooling-prioritization question
    ↓
Agent generates Urban Heat Brief
    ↓
Replay Brief includes FortyGuard evidence and explicitly excludes current NWS context
    ↓
Journalist reads the concise, attributed narrative
    ↓
Publication can cite the displayed FortyGuard source and Replay observation time
```

### 2.4 Resident Journey

```
Open app
    ↓
Query: "Is it safe outside?"
    ↓
Agent checks: FortyGuard temperature + NWS advisory (LIVE only)
    ↓
Agent responds: "NWS has issued an Extreme Heat Warning. Temperature is 42°C."
    ↓
Agent presents Urban Heat Brief with attributed sources
    ↓
Resident gets actionable information
```

---

## 3. Interaction Patterns

### 3.1 Conversational Exploration

```
User: "What's the heat risk in Phoenix?"
Agent: [ranks top-3 with evidence, Urban Heat Brief displayed]
User: "Why are the candidates tied?"
Agent: [shows near-tie explanation within the Brief]
User: "Give me a brief I can share"
Agent: [Brief is already displayed with full attribution]
```

### 3.2 Direct Dashboard Interaction

```
User opens map
    ↓
Heat overlay displays FortyGuard data
    ↓
User clicks a location
    ↓
Agent retrieves environmental parameters
    ↓
Agent displays ranking and evidence
    ↓
User clicks "Why?"
    ↓
Evidence panel opens
```

### 3.3 Mode Switching

```
User starts in REPLAY mode (default)
    ↓
User explores product with fixture data
    ↓
User switches to LIVE mode
    ↓
Agent re-queries with live FortyGuard API
    ↓
All data now labeled "Live"
    ↓
Evidence chain updated with live receipts
```

---

## 4. What Each User Expects

| User | Expects | Must Not See |
|------|---------|-------------|
| City Planner | Ranked locations with evidence | Unranked temperature list |
| Emergency Manager | Current conditions + advisory | Historical data without context |
| Journalist | Ready-to-publish brief | Raw API responses |
| Resident | Plain-language assessment | Technical jargon |
| Judge | Evidence chain + provenance | Fabricated or unattributed claims |

---

## 5. Failure Journey

```
User queries
    ↓
FortyGuard unavailable
    ↓
Agent responds: "FortyGuard data is currently unavailable. Cannot generate analysis."
    ↓
No invented temperature data
    ↓
No fallback to other sources for temperature
    ↓
Clear error state with explanation
```

```
User queries
    ↓
FortyGuard available, NWS unavailable
    ↓
Agent responds with FortyGuard analysis
    ↓
Agent notes: "NWS data is not currently available."
    ↓
Brief omits NWS section
    ↓
No invented weather conditions
```

---

## 6. QA Implications

| Journey | QA Test Area |
|---------|-------------|
| City Planner | SPEC-009 ranking, SPEC-010 intervention |
| Emergency Manager | NWS integration, real-time response |
| Journalist | Heat Brief correctness, attribution |
| Resident | Plain-language assessment, cooling centre info |
| Judge | Evidence chain, provenance, mode integrity |
| All | Failure handling, graceful degradation |

---

*This document explains user interaction patterns to a fresh agent. It enables QA-Pilot to test realistic user scenarios.*
