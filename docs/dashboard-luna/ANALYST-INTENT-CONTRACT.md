# Analyst Intent Contract

The analyst parses user language deterministically against the loaded governed state. Registry intents: priority, compare candidates, near tie, canopy, parks, current weather/NWS, evidence/provenance, map navigation, heat relief, historical context, and unsupported intervention efficacy.

Each intent has keywords, a payload-derived answer builder, source-role disclosure, optional UI action, and follow-up suggestions. No canned real-world values, external LLM, browser provider calls, persistence, or second ranking model are used. Replay answers explicitly disclose that current NWS is excluded; Phoenix GIS is always context-only.

## P1-R1 Amendments

### Bounded unsupported semantics

Unknown or unrecognized input MUST NOT:
- silently become mode-switch;
- silently become another supported intent;
- trigger Replay;
- fabricate a generic answer.

Unknown input returns a bounded unsupported/not-understood answer with examples of supported questions.

### Question catalogue

The dashboard exposes a discoverable catalogue/suggestion surface for supported questions, including (but not limited to):
- Where should Phoenix prioritize cooling?
- Compare the three candidates.
- Why are these locations nearly tied?
- What was the weather that afternoon?
- Were there heat alerts?
- What was happening in Phoenix that day?
- Show relevant reporting from that day.
- Compare tree canopy.
- Which candidates are near parks?
- Where can someone near Candidate N find heat relief?
- Where did this evidence come from?
- What can this analysis not tell me?
- Focus Candidate N.

### FortyGuard connection in analyst answers

Every contextual answer semantically communicates:
- **DIRECT ANSWER** — what the requested evidence says;
- **FORTYGUARD CONNECTION** — how local measured thermal evidence makes the answer spatially actionable;
- **CONTEXT** — what NWS/GIS/reporting/Heat Relief contributes;
- **BOUNDARY** — what the evidence does not establish.

Natural prose is preferred; four literal headings are not required. Contextual evidence never changes ranking.
