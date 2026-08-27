# Urban Heat Intelligence — Submission Summary

**Track:** 6 — Agentic Track (API + Agentic)
**Team:** urban-heat-intelligence
**Hackathon:** FortyGuard Hackathon '26

---

## The Problem

Phoenix experiences extreme urban heat. City planners, emergency managers, and journalists need to know where to prioritize cooling intervention — but raw temperature data alone doesn't answer that question. The harder problem is interpreting thermal evidence into actionable, attributable decision support.

## The Product

Urban Heat Intelligence is an evidence-backed heat decision-support agent. Ask "Where should Phoenix prioritize a cooling intervention this afternoon?" and the agent:

1. Calls **FortyGuard's Temperature API** (`POST /v1/heatmap`) to evaluate 367 thermal features across the queried Phoenix area at 2-meter resolution
2. Ranks the top-3 candidate locations by observed thermal burden
3. Calls **FortyGuard Environmental Parameters** (`POST /v1/env_params`) for each candidate — retrieving heat index, apparent temperature, and humidity
4. Identifies near-tied candidates (within 0.1°C) and states this honestly rather than fabricating a false distinction
5. Composes an **Urban Heat Brief** — a concise, source-attributed narrative suitable for planners, journalists, or residents
6. Presents an inspectable evidence chain showing every step from question to answer

## FortyGuard as Central Platform

FortyGuard is the primary and required data source. The product cannot function without it. The async workflow (POST → activity_id → poll GET) is the foundation of every analysis. NWS weather context is optional supplementary data in LIVE mode only — never used for thermal ranking.

## Agentic Behavior

The agent plans tool selection based on question intent (cooling_prioritization vs. area_risk_assessment vs. temperature_distribution), orchestrates FortyGuard API calls, composes comparative evidence across candidates, and generates a human-readable brief with claim-level provenance. Every factual sentence in the Brief is traceable to a specific evidence node.

## Replay vs. LIVE

**Replay** uses genuine FortyGuard API responses recorded on August 25, 2026 — zero network calls, deterministic, fixture-verified. **LIVE** executes real FortyGuard API calls with the user's credential. The two modes are never silently mixed. Current NWS context is explicitly excluded from Replay to preserve provenance integrity.

## Measured Result

The Replay demonstration shows 367 thermal features with an area mean of approximately 42.03°C. The leading candidate measures approximately 42.05°C against an area mean of 42.03°C, with an apparent temperature of 46.4°C. Three candidates fall within the 0.1°C near-tie tolerance — the product states this honestly.

## Qualification

The product was independently qualified by QA-Pilot — **QUALIFIED_WITH_KNOWN_LIMITATIONS**. Known limitations include: full intervention-opportunity model deferred (requires GIS/demographic data not integrated), NWS not fetched in Replay (by design), and three-browser smoke not demonstrated (Chromium qualified). Zero product defects. Zero unsupported claims.

## Repository

Public GitHub repository with Python stdlib application (zero external dependencies), Playwright browser tests, and comprehensive test suites (91 tests across 6 suites).

**Public demo:** https://urban-heat-intelligence.onrender.com/
