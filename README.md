# Urban Heat Intelligence — FortyGuard Hackathon '26

> An evidence-backed heat decision support agent — ask a question about urban heat in natural language, get an answer built from FortyGuard temperature data, retrieved safety knowledge, and visible reasoning, all wrapped in a receipt showing exactly where every number came from.

**Track:** 6 — Agentic Track (API + Agentic)

## What It Does

Ask a question like "What's the heat risk for construction workers in Phoenix right now?" and the agent:

1. Calls FortyGuard's Temperature API for live observations (2m resolution)
2. Retrieves relevant passages from heat-safety literature (WHO, OSHA, city guidelines)
3. Returns an answer with a full evidence chain: data source, retrieved references, and a receipt

Every answer carries a receipt — the data source, the reasoning, the confidence.

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd hackathon26

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your FortyGuard API key

# Run the agent
python -m src.main
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent | Python |
| Temperature API | FortyGuard Temperature API |
| Database | SQLite + sqlite-vec |
| Interface | HTML + TypeScript |

## How to Demo

1. Start the application
2. Ask: "What's the heat risk in downtown Phoenix right now?"
3. Observe: agent calls FortyGuard API, retrieves safety knowledge, returns answer with receipt
4. Ask: "What should construction workers know about this heat level?"
5. Observe: agent connects temperature to OSHA/WHO guidance with source citations

## API Provenance

- **Temperature data:** FortyGuard Temperature API (2m resolution, U.S. locations)
- **Safety knowledge:** OSHA Heat Illness Prevention Guide, WHO Heat Health Guidance
- **Every answer** includes a structured receipt showing data source, timestamp, and confidence

## License

Built for the FortyGuard Hackathon '26. See hackathon terms for usage rights.
