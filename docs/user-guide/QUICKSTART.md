# Urban Heat Intelligence — Developer Quick Start

**CANDIDATE — not canonical until Owner acceptance**

---

## Prerequisites

- Python 3.10 or later
- No external dependencies — the product uses only Python standard library modules
- A web browser (for the dashboard)
- Optional: FortyGuard API key (for Live mode)

---

## Clone and Run

```bash
# Clone the repository
git clone <repository-url>
cd urban-heat-intelligence

# Run the server
python3 app/server.py
```

Open your browser to the URL displayed by the server (typically `http://localhost:8000`).

---

## What Works Immediately

**Replay mode** works out of the box with zero configuration. It uses pre-recorded genuine FortyGuard API responses from August 25, 2026.

Open the browser, and you can:
- Query Phoenix thermal data
- View ranked priority locations
- Read the Urban Heat Brief
- Explore the evidence chain ("Why?" panel)
- Toggle between Live and Replay modes

---

## Live Mode Setup

To use Live mode with real-time FortyGuard data, you need an API key.

### Option 1: Environment Variable

```bash
export FORTYGUARD_API_KEY="your-api-key-here"
python3 app/server.py
```

### Option 2: Secrets File

Create the file `.secrets/fortyguard.env` in the project root:

```
FORTYGUARD_API_KEY=your-api-key-here
```

The product reads from this file automatically. Never commit this file to version control.

---

## Deploy to Render

The product is configured for deployment on Render:

1. Push your repository to GitHub
2. Connect the repository to Render
3. Render detects the configuration and deploys automatically
4. The public URL is your Live deployment

The deployment uses the same `python3 app/server.py` entry point.

---

## Project Structure

```
app/
  server.py          # Entry point — run this
  ...                # Application modules
fixtures/
  ...                # Pre-recorded FortyGuard responses (Replay mode)
.secrets/
  fortyguard.env     # API key (optional, not committed)
```

---

## Key Technical Details

- **Stack:** Python 3.10+ stdlib only — no pip install required
- **Dashboard:** Leaflet.js heat overlay with click-to-query
- **Architecture:** Three layers — Server, Agent + Decision Engine, Interface
- **Evidence:** Every tool call produces an evidence receipt in the in-memory evidence chain, returned in the JSON API response
- **Modes:** Live and Replay data never contaminate each other

---

*This document is CANDIDATE — not canonical until Owner acceptance.*
